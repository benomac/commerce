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
    ############# make it so you only have to render web page once, just change th e variables!!!!!!!!!!
    try:
        logged_in_user = request.user
        item = AuctionListing.objects.get(pk=listing_id)
        print(item.item)
        error = False
        watch_message = False
        bidder = User.objects.get(username=logged_in_user)
        
        
        if logged_in_user == item.user:
            return render(request, "auctions/listing.html", {
                "item_owner": True, "item": item
            })

        if request.method == "POST":    
            print("passed1")
            # get bid amount from form and add it to 'form' variable
            form = NewBid(request.POST)
            
            if form.is_valid():
                print("passed2")
                # Extract amount from form variable
                amount = form.cleaned_data["amount"]
                try:
                    currant_bid = Bid.objects.get(bid_item=item)
                    print("passed3", currant_bid.bid)
                    print(currant_bid)
                    if amount > currant_bid.bid:
                        Bid.objects.get(bid_item=item).delete()
                        bid = Bid.objects.create(bid=amount, bidder=bidder, bid_item=item)
                        bid.save()
                        # currant_bid.save
                        print("new_bid")
                        return render(request, "auctions/listing.html", {
                "newbidform": NewBid(), "item": item, "message": watch_message, "error": error
                
            })
                    else:
                        print("3b")
                        error = True
                        return render(request, "auctions/listing.html", {
                "newbidform": NewBid(), "item": item, "message": watch_message, "error": error
                
            })
                
                except:
                    # check if bid is higher than starting bid
                    print("passed4")
                    if amount >= item.starting_bid:
                        bid = Bid.objects.create(bid=amount, bidder=bidder, bid_item=item)
                        bid.save()
                        return render(request, "auctions/listing.html", {
                "newbidform": NewBid(), "item": item, "message": watch_message
                
            })
                    else:
                        error = True
                        print("passed5")
                        return render(request, "auctions/listing.html", {
                "newbidform": NewBid(), "item": item, "message": watch_message, "error": error
                
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
                "newbidform": NewBid(), "item": item
            })

