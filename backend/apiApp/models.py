from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid
from django.utils.timezone import now


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="category", blank=True, null=True)
    icon = models.ImageField(upload_to="category_icon", blank=True, null=True)
    featured = models.BooleanField(default=False)
    position = models.IntegerField(default=0)  
    on_del = models.BooleanField(default=False)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug
        
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, blank=True, default=uuid.uuid4)
    details = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    posted_in = models.CharField(max_length=255)
    featured_image = models.ImageField(upload_to="product_img", blank=True, null=True)
    posted_date = models.DateField(default=now, blank=True)
    featured = models.BooleanField(default=False) 
    position = models.IntegerField(default=0)
    on_del = models.BooleanField(default=False)
    owner_picture = models.URLField(blank=True, null=True)
    owner_email = models.EmailField(blank=True, null=True)

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="products",  blank=True, null=True)

    def __str__(self):
        return self.name
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return str(self.id)


class Chat(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_as_buyer')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_as_seller')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        super().save(*args, **kwargs)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.sender.email} ->  {self.text[:20]}"

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')