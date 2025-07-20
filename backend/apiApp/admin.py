from django.contrib import admin
from .models import CustomUser, Product, Category, Wishlist, Chat, Message, ProductImage
from django.contrib.auth.admin import UserAdmin



class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
admin.site.register(CustomUser, CustomUserAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price'] 
admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'name' )
admin.site.register(Category, CategoryAdmin)


admin.site.register([Chat])
admin.site.register([Message])
admin.site.register([Wishlist])
admin.site.register([ProductImage])