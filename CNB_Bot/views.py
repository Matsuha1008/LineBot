from django.shortcuts import render, redirect
from django.http import request, HttpRequest,  HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

from django.conf import settings

from .models.users import User_Info

from .products import list_all



# 取得 setting.py 中 LINE Bot 的憑證
# 進行 Messaging API 的驗證
# 建立解析器 parser
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


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


        
# 建立 user 資料
def get_or_create_user(user_id):
    # 先從 user_id 搜尋
    user = User_Info.objects.filter(user_id=user_id).first()
    # 若資料庫尚無該 user 資料
    if not user:
        profile = line_bot_api.get_profile(user_id)
        # 建立資料
        User_Info.objects.create(user_id=user_id,
                                 name=profile.display_name,
                                 image_url=profile.picture_url)

    return user



# 處理 event
def handle_event(body, signature):
    events = parser.parse(body, signature)
    
    # 取出 events 中的資料
    for event in events:
        get_or_create_user(event.source.user_id)

        # 判斷
        # 若 event 為 message 訊息
        if isinstance(event, MessageEvent):
            handle_message(event)

        # 若 event 為 follow
        elif isinstance(event, FollowEvent):
           line_bot_api.reply_message(event.reply_token)
    
        # 若 event 為解除 follow
        elif isinstance(event, UnfollowEvent):
           line_bot_api.reply_message(event.reply_token)  

        else:
            return HttpResponseBadRequest()


def handle_message(event):
    message_text = str(event.message.text).lower()
    message = []

    # 圖文選單：關於
    if message_text in ['關於', 'about']:

        message = [
            TextSendMessage(
                '您好～感謝您的訊息。'
                ), 

            TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='About',
                                text='C&B是使用Python + Django開發的線上商店專案。歡迎點擊下方連結以瞭解更多。',
                                actions=[
                                    URITemplateAction(
                                        type='uri',
                                        label='開發者日誌',
                                        uri=' '),
                                    URITemplateAction(
                                        type='uri',
                                        label='Github',
                                        uri='https://github.com/Matsuha1008'),
                                        ])),          

            StickerSendMessage(
                package_id='11539',
                sticker_id='52114110')
        ]
        
        line_bot_api.reply_message(event.reply_token, message)

        
    # 圖文選單：質感選物
    elif message_text in ['質感選物', '選物', '商品分類', '分類']:
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

        line_bot_api.reply_message(event.reply_token, message)


    # 選擇商品分類
    elif message_text in ['晶礦', '文具']:
        text = message_text
        message.append(list_all(text))

        line_bot_api.reply_message(event.reply_token, message)



    # 圖文選單：我的商品
    elif message_text in ['我的商品', '我的', '商品']:
        message = "購物車功能尚在開發中"
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
