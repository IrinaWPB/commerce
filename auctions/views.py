from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max

from .models import User, Listing, Bid, Category, Comment, Watchlist, Bought
from .forms import NewTitle



def index(request):
    queryset = Listing.objects.all()

    #If user is authorized - adding watchlist count to the index page
    user = request.user
    allusers =  User.objects.all()
    if user in allusers:
        count = Watchlist.objects.filter(user = request.user).count()
        context = {
            "object_list":queryset,
            "count": count
        }    
        return render(request, "auctions/index.html", context)
    else:
        context = {
            "object_list":queryset
        }    
        return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
  
def create(request): 
    # Watchlist count
    count = Watchlist.objects.filter(user = request.user).count()
    
    # Creating a new listing
    if request.method == "POST":
        form = NewTitle(request.POST)
        if form.is_valid():
            title = request.POST.get("title")
            cat_id = request.POST.get("category")
            category = Category.objects.get(id=cat_id)
            picture = request.POST.get("picture")
            description = request.POST.get("description")
            price = request.POST.get("price")
            listing = Listing.objects.create(title=title, category=category, picture = picture, description = description, price=price, creator = request.user)       
            return HttpResponseRedirect(reverse("index"))      
    else:  
        form = NewTitle()        
        context = {
            "form": form,
            "count": count
        }
        return render(request, "auctions/create.html", context)

def add_comment(request, id):
    count = Watchlist.objects.filter(user = request.user).count()
    listing = get_object_or_404(Listing, id=id)

    # If posted by different user - option to add a comment
    if listing.creator != request.user:

        # Creating a new comment, adding to the listing
        if request.method == "POST": 
            comment = request.POST.get('comment')
            user = request.user
            product = Listing.objects.get(title = listing.title)
            new_comment = Comment.objects.create(comment=comment, user = user, product = product)
            new_comment.save()
            comments = Comment.objects.filter(product = listing.id).order_by('-timestamp')
            return render(request, "auctions/listing.html", {
                "message_comment_added": "Your review was successfully added.",
                "object": listing,
                "comments": comments,
                "count": count
                })
        else:
            return render(request, "auctions/comments.html", {"object": listing })  
    else:
        return render(request, "auctions/comments.html", {"object": listing }) 

    
         
def listing_view(request, id):

    # Login required for listing details
    user = request.user
    allusers =  User.objects.all()
    if user not in allusers:
        return render(request, "auctions/index.html", 
            {"message_login": "Please register or/and log in for listing details."})
    obj = get_object_or_404(Listing, id=id)
    comments = Comment.objects.filter(product = obj.id).order_by('-timestamp')
    count = Watchlist.objects.filter(user = request.user).count()

    # Assigning "watched/not watched" value to the listing
    try:
        item = Watchlist.objects.get(product = obj, user = user)
    except ObjectDoesNotExist:
        item = None    
    if (item not in Watchlist.objects.filter(user = user)) or item == None:
        watched = False  
    else:
        watched = True  

    # Adding a new bid       
    if request.method == "POST" and "bid" in request.POST:
        price = obj.price
        bid = request.POST.get('bid')

        # Checking if the bid is valid
        if int(float(bid)) > int(price):
            obj.price = float(bid)
            obj.save()
            newbid = Bid.objects.create(bid = bid, user = request.user, title = obj) 
            newbid.save() 

        # If not - request to provide a valid bid      
        else: 
            return render(request, "auctions/listing.html", {
                "message_valid_bid": "Enter valid bid.",
                "object": obj,
                "count": count,
                "comments": comments, 
                "watched": watched
                 })  
    
    # Adding to watchlist if the item is not on the user's watchlist
    if request.method == "POST" and "add" in request.POST:
            if not user.watchlist.filter(product=obj):
                watchlist = Watchlist()
                watchlist.user = request.user
                watchlist.product = obj
                watchlist.save()
                watched = True
            return render(request, "auctions/listing.html", {
                "message_add": "This item was added to your Watchlist",
                "object": obj,
                "count": count,
                "comments": comments,
                "watched": watched
            })   
    # Removing from user's watchlist if the item is there.         
    elif request.method == "POST" and "delete" in request.POST: 
            user.watchlist.filter(product=obj).delete()
            watched = False
            return render(request, "auctions/listing.html", {
                "message_delete": "This item was removed from your Watchlist",
                "object": obj,
                "count": count,
                "comments": comments, 
                "watched": watched
            })
    # Closing the auction
    elif request.method == "POST" and "close" in request.POST:

        # Removing from database if no bids
        item = Bid.objects.filter(title = obj)
        if not item:
            Listing.objects.filter(id=id).delete()      
            return HttpResponseRedirect(reverse("index"))
        
        # Calculating the winner    
        else:
            # Finding the largest bid #
            bids = Bid.objects.filter(title = obj).order_by('-bid')  
            highest_bid = bids[0] 

            # Adding to the Sold database
            closeditem = Bought.objects.create(item = obj, seller = obj.creator, winner = bids[0].user)
            closeditem.save()
            return render(request, "auctions/listing.html", {
                "message_closed": "You have closed the auction. The winner is:", 
                "closeditem": closeditem,
                "object": obj,
                "count": count
                })
     # Adding the "sold" message to the listing
    if obj.id in Bought.objects.values_list('item', flat = True):
        Watchlist.objects.filter(id=id).delete()
        closeditem = Bought.objects.get(item = obj)
        return render(request, "auctions/listing.html", {
                "message_sold_winner": "Congratulations! You won this item.",
                "message_sold": "This item is sold. The listing is no longer active.",
                "object": obj,
                "comments": comments,
                "winner": closeditem.winner,
                "closeditem": closeditem
                 })

    return render(request, "auctions/listing.html", {
                "object": obj,
                "count": count,
                "comments": comments,
                "watched": watched
               
            })
    
def categories_view(request):
    queryset = Category.objects.all() 
    count = Watchlist.objects.filter(user = request.user).count()
    context = {
        "object_list": queryset,
        "count" : count,
    }
    return render(request, "auctions/categories.html", context)

def category_view(request, id):
    count = Watchlist.objects.filter(user = request.user).count()
    obj = get_object_or_404(Category, id=id)

    # List of objects in the requested category
    listing_list = Listing.objects.filter(category = obj)
    context = {
        "object": obj,
        "listing": listing_list,
        "count": count
    }
    return render(request, "auctions/category.html", context)

def watchlist_view(request):
    count = Watchlist.objects.filter(user = request.user).count()
    watchlist = Watchlist.objects.filter(user = request.user)
    context = {
        "watchlist" : watchlist,
        "count": count
    }    
    return render(request, "auctions/watchlist.html", context)

# Additional function. Shows user's won auctions and sold and posted items.
def my_account_view(request):
    posted = Listing.objects.filter(creator = request.user)
    won = Bought.objects.filter(winner = request.user)
    sold = Bought.objects.filter(seller = request.user)
    count = Watchlist.objects.filter(user = request.user).count()  
    context = {
        "posted": posted,
        "won" : won,
        "sold" : sold,
        "count": count
    }
    return render(request, "auctions/myaccount.html", context)    


