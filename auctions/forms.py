from django import forms
from utils import CATEGORIES
CATEGORIES1 = CATEGORIES

class NewListingForm(forms.Form):
    title = forms.CharField(label="Item title")
    category = forms.ChoiceField(widget=forms.Select, choices=CATEGORIES1, required=False)
    image = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea())
    starting_bid = forms.FloatField()

class NewBid(forms.Form):
    Bid_amount = forms.FloatField()

class Comments(forms.Form):
    comment = forms.CharField(label="Comment")
    
