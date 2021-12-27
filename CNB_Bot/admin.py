from django.contrib import admin

from .models.users import User_Info
from .models.products import Products, Category
from .models.orders import Orders, Items



# User_Info_Admin
class User_Info_Admin(admin.ModelAdmin):
    list_display = ('user_id','name','image_url', 'created_time') 
admin.site.register(User_Info, User_Info_Admin)



# Category
admin.site.register(Category)

# Products
class Product_Admin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'description', 'created_time')
admin.site.register(Products, Product_Admin)



# Orders
class Product_Admin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'amount', 'is_pay', 'transaction_id', 'created_time')
admin.site.register(Orders)

# Items
class Product_Admin(admin.ModelAdmin):
    list_display = ('transaction_id', 'created_time')
admin.site.register(Items)
