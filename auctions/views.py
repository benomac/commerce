from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, AuctionListing, WatchList, Bid, Comment
from .forms import NewListingForm, NewBid, Comments
from utils import CATEGORIES

def index(request):
    
    return render(request, "auctions/index.html", {
        "items": AuctionListing.objects.all()
    })


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

def new_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            # Get data from form
            # Argument in [] HAS to be form element name!!
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            user = request.user
            print("USER", user)
            # Create a new insert into the table
            new_listing_insert = AuctionListing.objects.create(item=title, description=description,
            starting_bid=starting_bid, image=image, category=category, user=user)
            new_listing_insert.save()

    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })

def listing(request, listing_id):
    user = request.user
    item = AuctionListing.objects.get(pk=listing_id)
    message = False
    comments = False
    
       
    # code for watch button, Working!
    
    if request.method == "POST":
        # If 'watch' button pressed do this:
        if "Watch" in request.POST:
            watched = WatchList.objects.create(watching=item, watcher=user)
            watched.save()
        # If 'unwatch' buttn pressed do this:
        if "unWatch" in request.POST:
            WatchList.objects.filter(watching=item, watcher=user).delete()
        
        # If 'close' button pressed do this:
        if "close" in request.POST:
            if Bid.objects.filter(bid_item=item).exists():
                winner = Bid.objects.get(bid_item=item).bidder_id
                Bid.objects.filter(bid_item=item).update(winner_id=winner)
        
        # Gets bid from bid form, checks whether it is greater than current bid and starting_bid
        # if not return message to user telling them so. If it is, it gets added to 
        # the bids table
        if "bidding" in request.POST:
            form = NewBid(request.POST)
            
            if form.is_valid():
                amount = form.cleaned_data["amount"]
                
            if not Bid.objects.filter(bid_item=item).exists() and amount >= item.starting_bid:
                new_bid = Bid.objects.create(bid=amount, bid_item=item, bidder=user)
                new_bid.save()
            
            elif Bid.objects.filter(bid_item=item).exists() and Bid.objects.filter(bid_item=item)[0].bid < amount:
                Bid.objects.filter(bid_item=item).update(bid=amount, bidder=user, bid_item=item)
            else:
                message = True
        
        # Takes comment and adds it to the comments table
        if "comment" in request.POST:
            form = Comments(request.POST)
            if form.is_valid():
                comment = form.cleaned_data["comment"]
                new_comment = Comment.objects.create(comment=comment, commented_item=item, user_commented=user)
                new_comment.save()
    
    # checks if any bids have been made on the 'item'
    try:
        bid = Bid.objects.get(bid_item=item).bid 
    except:
        bid = False
    
    # checks if there is a winner, will also mean the auction is closed, if so
    try:
        winner = Bid.objects.filter(bid_item=item)[0].winner
    except:
        winner = False

    # checks for any comments for 'item'
    if Comment.objects.filter(commented_item=item):
        comments = Comment.objects.filter(commented_item=item)

    # checks if user is logged in, not a great way of doing it though, DRY!     
    if not User.objects.filter(username=user).exists():
        return render(request, "auctions/listing.html", {
                    "item": item, "isuser": False, "price": bid, "user_comments": comments
                })
    else:
        print(comments)
        return render(request, "auctions/listing.html", {
            "owner": item.user, "form": NewBid(), "item": item, 
            "user": user, "watched": WatchList.objects.filter(watching=item, watcher=user), 
            "isuser": True, "message": message, "price": bid, "winner": winner, 
            "comments": Comments(), "user_comments": comments
        })

def watching(request):
    user = request.user
    users_watched_items = [AuctionListing.objects.get(item=i.watching) for i in user.user.all()]
    
    return render(request, "auctions/watching.html", {
        "watching": users_watched_items
    })

def categories(request):
    dic = {}
    for i in AuctionListing.objects.all():
        if i.category not in dic:
            dic[i.category] = [i.item]
        else:
            dic[i.category].append(i.item)
    # cats = [i[0] for i in CATEGORIES]
    # {% for i, j in dic.items %}
    #     {{i}}
    #     <br>
    #     {% for h in j %}
    #     {{h}}
    #     <br>
    #     {% endfor %}
    #     <br>
    #     <br>
    # {% endfor %}
    return render(request, "auctions/categories.html", {
        "dic": dic,  "categories": CATEGORIES
    })

def categories_contents(request, categoryName):
    user = request.user
    cat = CATEGORIES[categoryName]
    print(cat)
    items_in_category = AuctionListing.objects.filter(category=cat[1])
    
    print(items_in_category[0].user)
    return render(request, "auctions/categories_contents.html", {
        "cat": cat, "items": items_in_category, "user": user
    })