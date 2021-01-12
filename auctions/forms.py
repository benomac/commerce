from django import forms

class NewListingForm(forms.Form):
    title = forms.CharField(label="Item title")
    category = forms.CharField(required=False)
    image = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea())
    starting_bid = forms.FloatField()

class NewBid(forms.Form):
    amount = forms.FloatField()
    
