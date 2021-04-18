from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.forms import ModelForm
from django import forms
 

class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.category}"

    def get_absolute_url(self):
        return f"/auctions/{self.id}"      


class Listing(models.Model):
    title = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    picture = models.URLField(null=True)
    description = models.TextField(max_length=256)
    timestamp = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return f"/auctions/{self.id}"    
            

class Watchlist(models.Model):
    product = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "watchlist")

    def __str__(self):
        return f"User {self.user} is watching {self.product}"
    
    
class Bid(models.Model):
    bid = models.DecimalField(max_digits=5, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Listing, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
   
    def __str__(self):
        return f"User {self.user} placed a bid {self.bid} on {self.title} on {self.timestamp}"


class Comment(models.Model):
    comment = models.TextField()   
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    product = models.ForeignKey(Listing, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f"User {self.user} left a comment {self.comment} on {self.product} on {self.timestamp}"
    
    def get_absolute_url(self):
        return f"/comments/{self.id}"  

class Bought(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)  
    timestamp = models.DateTimeField(default=timezone.now) 
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder") 

    def __str__(self):
        return f"User {self.winner} bought {self.item}  on {self.timestamp}. Seller: {self.seller}"   