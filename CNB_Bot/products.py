from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

from urllib.parse import quote

from django.conf import settings

from django.views.static import serve
from .models.products import Category, Products

import os


def list_all(text):
    #將JSON設定為變數content，並以FlexSendMessage()包成Flex Message
    url = 'https://cnb-linebot.herokuapp.com/'
    if text == '晶礦':
      products = Products.objects.filter(category=1)
    
    elif text == '文具':
      products = Products.objects.filter(category=2)


    content = {"type": "carousel",
               "contents": []}

    for product in products:
  
      bubble ={"type": "bubble",
               "hero": {"type": "image",
                        "size": "full",
                        "aspectRatio": "1:1",
                        "aspectMode": "cover",
                        "url": product.image_url},# 商品圖片

               "body": {"type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [{"type": "text",
                                      "text": product.name,# 商品名稱
                                      "wrap": True,
                                      "weight": "bold",
                                      "size": "xl"},
                                      {"type": "box",
                                      "layout": "baseline",
                                      "contents": [{"type": "text",
                                                    "text": "NT${price}".format(price=product.price),# 商品價格
                                                    "wrap": True,
                                                    "weight": "bold",
                                                    "size": "xl",
                                                    "flex": 0}]},
                                     {"type": "text",
                                      "text": product.description,# 商品敘述
                                      "wrap": True,
                                      "size": "xxs",
                                      "margin": "md",
                                      "flex": 0}]},
               "footer": {"type": "box",
                          "layout": "vertical",
                          "spacing": "sm",
                          "contents": [{"type": "button",
                                        "style": "primary",
                                        "color": "#405f67",
                                        "action": {"type": "uri",
                                                   "label": "商品詳細",
                                                   "uri": 'line://oaMessage/{base_id}/?{message}'.format(base_id=settings.BASE_ID,
                                                                                                message=quote("購買{product}".format(product=product.name)))}}]}}

      content["contents"].append(bubble)

    message=FlexSendMessage(alt_text='商品列表',contents=content)
    return message