from rest_framework import serializers
from .models import Product, Category, Wishlist, Message, Chat, ProductImage, CustomUser
from django.contrib.auth import get_user_model



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username", "first_name", "last_name", "profile_picture_url"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'details', 'posted_in', 'posted_date', 'description', 'brand', 'category', 'owner', 'featured_image', 'featured', 'owner_picture', 'owner_email']



class ProductListSerializer(serializers.ModelSerializer):
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'details', 'posted_in', 'posted_date', 'description', 'brand','category', 'owner', 'featured_image', 'featured', 'is_wishlisted', 'owner_picture']

    def get_is_wishlisted(self, obj):
        user = self.context.get('user')
        if user and user.is_authenticated:
            return Wishlist.objects.filter(user=user, product=obj).exists()
        return False

    
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class OwnerSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username','email', 'profile_picture_url']

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    is_wishlisted = serializers.SerializerMethodField()
    

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'featured_image', 'price',
            'details', 'posted_in', 'posted_date', 'description',
            'category', 'featured', 'images', 'owner', 'is_wishlisted', 'owner_picture'
        ]

    def get_is_wishlisted(self, obj):
        user = self.context.get('user')
        if user and user.is_authenticated:
            return Wishlist.objects.filter(user=user, product=obj).exists()
        return False


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image", "slug", 'icon', 'position']

class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ["id", "name", "image", "products"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'slug', 'product',  'buyer', 'seller', 'last_message', 'messages']

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None


class WishlistSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Wishlist
        fields = ['id', 'product']