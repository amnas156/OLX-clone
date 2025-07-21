from django.urls import path
from . import views




urlpatterns = [
    path("create_user/", views.create_user, name="create_user"),
    path("existing_user/<str:email>", views.existing_user, name="existing_user"),
    path('post_product/', views.post_product, name='post_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='product-delete'),
    path('product_list', views.product_list, name='product_list'),
    path('fresh_recommendations/', views.fresh_recommendations, name='fresh_recommendations'),
    path('products/<slug:slug>', views.product_detail, name='product_detail'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete-product'),
    path('category_list', views.category_list, name='category_list'),
    path('category/<slug:slug>', views.category_detail, name='category_detail'),
    path('search/', views.product_search, name='search-products'),
    path('chats/start/', views.start_chat, name='start_chat'),
    path("chats/send/", views.send_message, name='send_message'),
    path("chats/<slug:slug>/", views.get_chat_by_slug, name='get_chat_by_slug'),
    path("chats/<str:email>/", views.get_chat_list, name='get_chat_list'),
    path('user-ads/<str:email>/', views.user_ads, name='user-ads'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/<str:email>/', views.wishlist_items, name='wishlist'),
]