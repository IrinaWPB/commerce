from django.contrib import admin

# Register your models here.
from .models import User, Category, Listing, Bid, Comment, Watchlist, Bought

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)
admin.site.register(Bought)