from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

from urllib.parse import parse_qsl
import uuid

from django.conf import settings

from .models.users import User_Info
from .models.products import Products
from .models.orders import Orders, Items

from .linepay import LinePay
from .products import list_all
from .cart import Cart



# 取得 setting.py 中 LINE Bot 的憑證
# 進行 Messaging API 的驗證
# 建立解析器 parser
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)



# 按下確認付款
def confirm(request):
    transaction_id = request.GET.get('transactionId')
    order = Orders.objects.filter(transaction_id=transaction_id).first()
    print(order)
    print(transaction_id)

    if order:
        order.is_pay = True # 訂單狀態改為已付款
        order.save()
        
        display_receipt(order)

        return render(request, 'is_pay.html')




# 確認伺服器狀態
@csrf_exempt
def callback(request):
    if request.method == 'POST':

        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('UTF-8')

        try:
            handle_event(body, signature)  
            
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
     
        return HttpResponse()


# 處理 event
def handle_event(body, signature):
    events = parser.parse(body, signature)
    
    # 取出 events 中的資料
    for event in events:
        # 判斷類型
        # 若為 MessageEvent
        if isinstance(event, MessageEvent):
            handle_message(event)

        # 若為 PostbackEvent
        elif isinstance(event, PostbackEvent):
            handle_postback(event)

        # 若為 FollowEvent
        elif isinstance(event, FollowEvent):
           line_bot_api.reply_message(event.reply_token)
    
        # 若為解除 UnfollowEvent
        elif isinstance(event, UnfollowEvent):
           line_bot_api.reply_message(event.reply_token)  

        else:
            return HttpResponseBadRequest()




# 建立 user 資料
def get_or_create_user(user_id):
    # 從 user_id 先搜尋
    user = User_Info.objects.filter(user_id=user_id).first()
    # 若尚無資料
    if not user:
        profile = line_bot_api.get_profile(user_id)
        # 建立 user 資料
        User_Info.objects.create(user_id=user_id,
                                 name=profile.display_name,
                                 image_url=profile.picture_url)

    return user



# 處理 MessageEvent
def handle_message(event):
    get_or_create_user(event.source.user_id)
    message_text = str(event.message.text).lower()
    cart = Cart(user_id = event.source.user_id)

    message = []

    # 圖文選單：關於
    if message_text in ['關於']:

        message = [
            TextSendMessage(
                '您好，感謝您的訊息～'
                ), 

            TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='About',
                                text='C&B是使用Python + Django開發的線上商店專案。歡迎點擊下方連結以瞭解更多。',
                                actions=[
                                    URITemplateAction(
                                        type='uri',
                                        label='開發者網站',
                                        uri=''),
                                    URITemplateAction(
                                        type='uri',
                                        label='GitHub',
                                        uri=''),
                                        ])),          

            StickerSendMessage(
                package_id='11539',
                sticker_id='52114110')
        ]


    # 圖文選單：質感選物
    elif message_text in ['質感選物', '選物', '商品分類', '分類', '繼續購物']:
        message =TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='C&B 質感選物',
                                text='請選擇商品分類',
                                actions=[
                                    MessageTemplateAction(
                                        label='晶礦',
                                        text='晶礦'
                                    ),
                                    MessageTemplateAction(
                                        label='文具',
                                        text='文具'
                                    )]))


    # 商品分類列表
    # list_all()
    elif message_text in ['晶礦', '文具']:
        text = message_text
        message.append(list_all(text))


    # 圖文選單：我的商品
    elif message_text in ['我的商品', '我的', '商品', '查看商品']:

        if cart.bucket():
            message = cart.display()
        else:
            message = TextSendMessage(text='您的購物車目前沒有商品')


    # 加入購物車
    elif "我要購買" in message_text:

        # 對 "我要購買 {product} × （請輸入數量）" 這則訊息進行切片
        # 第[1]個切片即為商品名稱
        # 第[3]個切片即為商品數量
        product_name = message_text.split(' ')[1]
        num_item = int(message_text.rsplit(' ')[3])

        # 查詢資料庫中是否存在該商品
        product = Products.objects.filter(name=product_name).first()

        # 商品存在，則加入購物車
        if product:
            cart.add(product=product_name, num=num_item)
            confirm_template = ConfirmTemplate(
                text='{}×{}　已為您加入購物車'.format(product_name, num_item),
                actions=[
                    MessageAction(label="查看商品", text="查看商品"),
                    PostbackAction(label='前往結帳',
                                              display_text='前往結帳',
                                              data='action=checkout')
                ])
            message = TemplateSendMessage(alt_text='還需要其他商品嗎？', template=confirm_template)

            
        else:
            message = TextSendMessage(text="查詢不到［{}］這項商品，請重新操作。".format(product_name))


        print(cart.bucket())



    elif message_text == '清空購物車':

        cart.reset()

        message = TextSendMessage(text='已為您清空購物車')
      

    # 測試用關鍵字：掐哩
    elif message_text in ['掐哩', '查理']:
        message = [
            ImageSendMessage(
                original_content_url='https://i.ytimg.com/vi/reg9Xxa7eIs/mqdefault.jpg',
                preview_image_url='https://i.ytimg.com/vi/reg9Xxa7eIs/mqdefault.jpg'
            )]

  
    if message:
        line_bot_api.reply_message(event.reply_token, message)

    


# 處理 PostbackEvent
def handle_postback(event):
    # 調用 parse_qsl() 解析參數
    data = dict(parse_qsl(event.postback.data))
    action = data.get('action')

    # 若 action 為 checkout，進入付款流程
    if action == 'checkout':

        user_id = event.source.user_id

        cart = Cart(user_id=user_id)

        if not cart.bucket():
            message = TextSendMessage(text='您的購物車目前沒有商品')

            line_bot_api.reply_message(event.reply_token, message)


        # 產生唯一識別碼 UUID
        # UUID4：亂數　hex：16進位
        order_id = uuid.uuid4().hex

        total = 0
        items = []

        # 從 cache 中取得
        for product_name, num in cart.bucket().items():
            product = Products.objects.filter(name=product_name).first()

            # 建立訂單中項目資料 dict
            item = {'product_id':product.id,
                    'product_name':product.name,
                    'product_price':product.price,
                    'order_id':order_id,
                    'quantity':num}

            items.append(item)

            total += product.price * int(num)
            print(items)
            print(total)



        # 建立資料後，必須清空 cache
        #cart.reset()

        # 建立 LinePay 物件
        line_pay = LinePay()
        

        # 建立訂單明細
        info = line_pay.pay(product_name='CNB_',
                            amount=total,
                            order_id=order_id,
                            product_image_url=settings.STORE_IMAGE_URL)
        pay_web_url = info['paymentUrl']['web']
        transaction_id = info['transactionId']


        # 建立 order 資料
        Orders.objects.create(id=order_id,
                              user_id=user_id,
                              amount=total,
                              is_pay=False,
                              transaction_id=transaction_id)
                              
        # 建立 item 資料
        for item in items:
            print(item)
            print(type(item))

            Items.objects.create(product_id = item['product_id'],
                                 product_name = item['product_name'],
                                 product_price = item['product_price'],
                                 order_id = item['order_id'],
                                 quantity = item['quantity'])
            #Items.objects.create(order_id=order_id)


        # 付款訊息
        button_template = ButtonsTemplate(
                 text='請確認金額：NT$ {}'.format(total),
                 actions=[
                    URIAction(label='LINE Pay 付款',
                              uri=pay_web_url)
                ])
        message = TemplateSendMessage(alt_text='請確認金額', template=button_template)


    else:
        message = TextSendMessage(text='麻煩您重新操作')

    line_bot_api.reply_message(event.reply_token, message)



# 自訂收據內容
def display_receipt(order):
    item_box_component = []
    # 訂單和詳細內容放在不同資料表中，需要先撈出來
    # 利用 order_id 過濾
    items = Items.objects.filter(order_id=order.id)

    # 一筆訂單可能會有多個商品，用 for 迴圈調出資料
    for item in items:
        item_box_component.append(BoxComponent(
            layout='horizontal',
            contents=[
                TextComponent(text='{product_name} × {quantity}'.
                              format(quantity=item.quantity,
                                     product_name=item.product_name),
                              size='sm',
                              color='#555555',
                              flex=0),
                TextComponent(text='NT${amount}'.
                              format(amount=(item.quantity * item.product_price)),
                              size='sm',
                              color='#111111',
                              align='end')]
            ))

        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='收據',
                                  weight='bold',
                                  color='#987a7a',
                                  size='sm'),
                    TextComponent(text='Crystal & Bright',
                                  weight='bold',
                                  color='#405f67',
                                  size='xxl',
                                  margin='md'),
                    TextComponent(text='- Online Store -',
                                  size='xs',
                                  color='#adadb0',
                                  wrap=True),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=item_box_component
                    ),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(text='TOTAL',
                                                  size='sm',
                                                  color='#555555',
                                                  flex=0),
                                    TextComponent(text='NT${total}'.
                                                  format(total=order.amount),
                                                  size='sm',
                                                  color='#111111',
                                                  align='end')]
                            )])],))

    message = FlexSendMessage(alt_text='收據', contents=bubble)

    line_bot_api.push_message(to=order.user_id, messages=message)
