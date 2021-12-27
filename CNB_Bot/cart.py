from cachelib import SimpleCache
from linebot.models import *

from .models.products import Products



cache = SimpleCache()


class Cart(object):
    # 初始化 cache
    def __init__(self, user_id):
        self.cache = cache
        self.user_id = user_id


    # 判斷購物車中是否存在商品
    def bucket(self):
        return cache.get(key=self.user_id)


    # 加入購物車
    def add(self, product, num):
        bucket = cache.get(key=self.user_id)#透過user_id取得使用者的購物車
        quantity = num
        # 購物車是空的　→　在空字典中加入一個字典 product: int(num)
        if bucket == None:
            cache.add(key=self.user_id, value={product: quantity})
        
        else:
            # 購物車已有東西　→　更新字典 product: int(num)
            bucket.update({product: quantity})
            # 再更新使用者的購物車
            cache.set(key=self.user_id, value=bucket)


    # 清空購物車
    def reset(self):
        cache.set(key=self.user_id, value={})


    # 展示購物車內容
    def display(self):#
        total = 0#總金額
        product_box_component = []#放置產品明細

        for product_name, num in self.bucket().items():
            #透過 Products.name 去搜尋
            product = Products.objects.filter(name=product_name).first()
            amount = product.price * int(num)#然後再乘以購買的數量
            total += amount

            #透過 TextComponent 顯示產品明細，透過BoxComponent包起來，再append到product_box_component中
            product_box_component.append(BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text='{product} x {num}'.format(product=product_name,
                                                                  num=num,),
                                  size='sm', color='#555555', flex=0),
                    TextComponent(text='NT$ {amount}'.format(amount=amount),
                                  size='sm', color='#111111', align='end')]
            ))

        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='以下是您訂購的商品',
                                  wrap=True,
                                  size='md'),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=product_box_component
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
                                    TextComponent(text='NT$ {total}'.format(total=total),
                                                  size='sm',
                                                  color='#111111',
                                                  align='end')]
                            )

                        ]
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='md',
                contents=[
                    ButtonComponent(
                        style='primary',
                        color='#405f67',
                        action=PostbackAction(label='前往結帳',
                                              display_text='前往結帳',
                                              data='action=checkout')
                    ),
                    BoxComponent(
                        layout='horizontal',
                        spacing='md',
                        contents=[
                            ButtonComponent(
                                style='primary',
                                color='#987a7a',
                                flex=1,
                                action=MessageAction(label='清空購物車',
                                                     text='清空購物車'),
                            ),
                            ButtonComponent(
                                style='primary',
                                color='#987a7a',
                                flex=1,
                                action=MessageAction(label='繼續購物',
                                                     text='繼續購物'),
                            )
                        ]

                    )
                ]
            )
        )

        message = FlexSendMessage(alt_text='Cart', contents=bubble)

        return message # 回傳到app.py message = cart.display()
