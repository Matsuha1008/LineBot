from django.contrib import admin

from .models.users import User_Info
from .models.products import Products, Category


# User_Info_Admin
class User_Info_Admin(admin.ModelAdmin):
    list_display = ('user_id','name','image_url', 'created_time')
    
admin.site.register(User_Info, User_Info_Admin)


# Products
class Product_Admin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'description', 'created_time')

admin.site.register(Products, Product_Admin)


# Category
admin.site.register(Category)

