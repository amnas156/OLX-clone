from django.shortcuts import render
from django.db import models
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import Product, Category, Wishlist, Message, CustomUser, Chat, ProductImage
from .serializers import ProductListSerializer, ProductSerializer, ProductDetailSerializer, CategoryListSerializer, CategoryDetailSerializer, WishlistSerializer, UserSerializer, MessageSerializer, ChatSerializer


User = get_user_model()


@api_view(["POST"])
def create_user(request):
    username = request.data.get("username")
    email = request.data.get("email")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    profile_picture_url = request.data.get("profile_picture_url")

    new_user = User.objects.create(username=username, email=email,
                                       first_name=first_name, last_name=last_name, profile_picture_url=profile_picture_url)
    serializer = UserSerializer(new_user)
    return Response(serializer.data)


@api_view(["GET"])
def existing_user(request, email):
    try:
        User.objects.get(email=email)
        return Response({"exists": True}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"exists": False}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def post_product(request):
    try:
        category_id = request.data.get('category_id')
        owner_email = request.data.get('owner_id')
        owner_picture_url = request.data.get('owner_picture_url')
        owner_email = request.data.get('owner_email')

        category = Category.objects.get(id=category_id)
        owner = CustomUser.objects.get(email=owner_email)  

        product = Product.objects.create(
            name=request.data.get('name'),
            description=request.data.get('description'),
            price=request.data.get('price'),
            details=request.data.get('details'),
            brand=request.data.get('brand'),
            posted_in=request.data.get('posted_in'),
            featured_image=request.FILES.get('images'), 
            owner_picture= owner_picture_url,
            category=category,
            owner=owner,
            owner_email=owner_email
        )
        
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return Response({'message': 'Product created successfully'})

    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
def user_ads(request, email):
    products = Product.objects.filter(owner_email=email).order_by('-posted_date')
    serializer = ProductDetailSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def fresh_recommendations(request):
    products = Product.objects.filter(on_del=False).order_by('-posted_date')[:12]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def product_list(request):
    products = Product.objects.filter(featured=True)
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def product_detail(request, slug):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)


@api_view(["GET"])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def category_post(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response({'detail': 'Product deleted.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def start_chat(request):
    product_id = request.data.get("product")
    buyer_email = request.data.get("buyer")
    
    if not product_id or not buyer_email:
        return Response({"error": "Product ID and Buyer email are required."}, status=400)

    product = get_object_or_404(Product, id=product_id)

    try:
        buyer = User.objects.get(email=buyer_email)
    except User.DoesNotExist:
        return Response({"error": "Buyer not found."}, status=404)

    seller = product.owner

    if buyer == seller:
        return Response({"error": "Cannot start chat with your own product."}, status=400)

    chat, created = Chat.objects.get_or_create(
        product=product,
        buyer=buyer,
        seller=seller
    )

    return Response(ChatSerializer(chat).data)


@api_view(["POST"])
def send_message(request):
    chat_id = request.data.get("chat_id")
    sender_email = request.data.get("sender_email")
    text = request.data.get("text")

    chat = Chat.objects.get(id=chat_id)
    sender = CustomUser.objects.get(email=sender_email)  

    message = Message.objects.create(chat=chat, sender=sender, text=text)
    serializer = MessageSerializer(message)
    return Response(serializer.data)


@api_view(['GET'])
def get_chat_by_slug(request, slug):
    chat = get_object_or_404(Chat, slug=slug)
    serializer = ChatSerializer(chat)
    return Response(serializer.data)


@api_view(['GET'])
def get_chat_list(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    chats = Chat.objects.filter(models.Q(buyer=user) | models.Q(seller=user))
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def toggle_wishlist(request):
    product_id = request.data.get("product_id")
    email = request.data.get("email")

    if not product_id or not email:
        return Response({"error": "Product ID and email are required."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)
    if not created:
        wishlist_item.delete()
        return Response({"status": "removed"})
    
    return Response({"status": "added"})


@api_view(['GET'])
def wishlist_items(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    wishlist_items = Wishlist.objects.filter(user=user).select_related('product')
    products = [item.product for item in wishlist_items]
    serialized = ProductSerializer(products, many=True, context={"request": request})
    return Response(serialized.data, status=status.HTTP_200_OK)