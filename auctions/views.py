from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, AuctionListing, WatchList, Bid
from .forms import NewListingForm, NewBid

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
    
    try:
        logged_in_user = request.user
        
        item = AuctionListing.objects.get(pk=listing_id)
        
        watch_message = False
        bidder = User.objects.get(username=logged_in_user)
        
        # if logged_in_user:
        #     if WatchList.objects.filter(watcher=logged_in_user).filter(watching=item):
        #         watch_message = True
        if logged_in_user == item.user:
            return render(request, "auctions/listing.html", {
                "item_owner": True, "item": item
            })

        if request.method == "POST":    
            form = NewBid(request.POST)
            if form.is_valid():
                amount = form.cleaned_data["amount"]
                print(logged_in_user)
                print(amount)
                print(type(bidder))
                print(item.id)
                if amount >= item.starting_bid:
                    
                    print("ITEM", type(item))
                    bid = Bid.objects.create(bid=amount, bidder=bidder, bid_item=item)
                    print("wtf")
                    bid.save()
                    return render(request, "auctions/new_listing.html", {
                        "form": NewListingForm()
                    })
                
            if 'watch' in request.POST:
                watching = WatchList.objects.create(watching=item, watcher=logged_in_user)
                watching.save()
                watch_message = True  
                
            elif 'unwatch' in request.POST:
                WatchList.objects.filter(watching=item).delete()
                watch_message = False    
        
        return render(request, "auctions/listing.html", {
                "newbidform": NewBid(), "item": item, "message": watch_message
                
            })
    except:
        return render(request, "auctions/listing.html", {
                "newbidform": NewBid(), "item": item, "message": watch_message
                
            })

