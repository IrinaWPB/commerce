from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("auctions/<str:id>", views.listing_view, name="listing"),
    path("categories", views.categories_view, name="categories"),
    path("categories/<str:id>", views.category_view, name="category"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("auctions/<str:id>/comments", views.add_comment, name="comments"),
    path("myaccount", views.my_account_view, name="myaccount")
    

]
