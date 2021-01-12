from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # items = models.ManyToManyField(AuctionListing, on_delete=models.SET_NULL, null=True, related_name="listing")
    
    def __str__(self):
        return f"{self.username}"

class AuctionListing(models.Model):
    category = models.CharField(max_length=64, default='SOME STRING')
    item = models.CharField(max_length=64)
    description = models.CharField(max_length=255)
    starting_bid = models.FloatField()
    # May have to make image max_length longer??
    image = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="owner")
    
    def __str__(self):
        return f"{self.item}"

class Bid(models.Model):
    bid = models.FloatField()
    bid_item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, null=True, related_name="buying")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidded")

class Comment(models.Model):
    comment = models.CharField(max_length=255)
    commented_item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="commented")
    user_commented = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usercomments")

class WatchList(models.Model):
    watching = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watching")
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    
    def __str__(self):
        return f"{self.watching}: {self.watcher_id}"