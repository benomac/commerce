from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, AuctionListing, WatchList, Bid
from .forms import NewListingForm, NewBid
from utils import test

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
    owner = item.user
    message = False
    print("user", user)
    # code for watch button, Working!
    if user:
        print("usertrue")
    else:
        print("userfalse")
    if request.method == "POST":
        if "Watch" in request.POST:
            watched = WatchList.objects.create(watching=item, watcher=user)
            watched.save()
        if "unWatch" in request.POST:
            WatchList.objects.filter(watching=item, watcher=user).delete()
        
        if "bidding" in request.POST:
            print("bidding")
            form = NewBid(request.POST)
            print(form)
            if form.is_valid():
                print("valid")
                amount = form.cleaned_data["amount"]
                print(amount, item)
                ### CHECK CHECK CHECK 
            if not Bid.objects.filter(bid_item=item).exists() and amount >= item.starting_bid:
                print("newbid")
                new_bid = Bid.objects.create(bid=amount, bid_item=item, bidder=user)
                new_bid.save()
            
            elif Bid.objects.filter(bid_item=item).exists() and Bid.objects.filter(bid_item=item)[0].bid < amount:
                print("change")
                Bid.objects.filter(bid_item=item).delete()
                update_bid = Bid.objects.create(bid=amount, bidder=user, bid_item=item)
                update_bid.save()
            else:
                message = True
            print("else")
                
        print("one")
        # return render(request, "auctions/listing.html", {
        #     "owner": owner, "form": NewBid(), "item": item, 
        #     "user": user, "watched": WatchList.objects.filter(watching=item, watcher=user), 
        #     "isuser": True, "message": message
        # })
    
        
    if not User.objects.filter(username=user).exists():
        return render(request, "auctions/listing.html", {
                    "item": item, "isuser": False    
                })
    else:
        print("else")
        return render(request, "auctions/listing.html", {
            "owner": owner, "form": NewBid(), "item": item, 
            "user": user, "watched": WatchList.objects.filter(watching=item, watcher=user), 
            "isuser": True, "message": message
        })