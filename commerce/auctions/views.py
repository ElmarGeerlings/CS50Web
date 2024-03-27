from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import ModelForm
from django import forms

from .models import User, AuctionListings, Bids, Comments, Watchlist

# Categories for listings
categories=[("Art","Art"), ("Clothes","Clothes"), ("Electronics","Electronics"), ("Home","Home"), ("Music","Music"), ("Sports","Sports"), ("Toys","Toys"), ("Other","Other")]

# List of active listings
def index(request):
    print(AuctionListings.objects.filter(active=1).order_by('-datetime'))
    return render(request, "auctions/index.html", {
        "title": "Active Listings",
        "listings": AuctionListings.objects.filter(active=1).order_by('-datetime')
    })

# Login menu
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

# Logout
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Register new user
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

# Create listing form
class CreateForm(ModelForm):
    title = forms.CharField(label="Title", required=True, widget=forms.TextInput(attrs={
                                                                            'placeholder': "Title",
                                                                            "autocomplete": "off",
                                                                            "aria-label": "title",
                                                                            "class": "form-control"
                                                                        }))
    description = forms.CharField(label="Description", required=True, widget=forms.Textarea(attrs={
                                    'placeholder': "Tell more about the product",
                                    'aria-label': "description",
                                    "class": "form-control"
                                    }))
    startingbid = forms.DecimalField(label='Starting Bid', required=True, widget=forms.NumberInput(attrs={
                                            'placeholder': 'Starting bid',
                                            'min': '0.01',
                                            'max': '99999999.99',
                                            'step': '0.01',
                                            'class': 'form-control'
                                        }))
    imageURL = forms.URLField(required=False, label="Image URL", widget=forms.URLInput(attrs={
                                        'placeholder': "Image URL",
                                        "class": "form-control"
                                    }))
    category = forms.ChoiceField(required=True, choices=categories, widget=forms.Select(attrs={
                                        'placeholder': "Choose category",
                                        "class": "form-control"
                                    }))
    class Meta:
        model = AuctionListings
        fields = ["title", "description", "startingbid", "imageURL", "category"]

# Let user create new listing
@login_required(login_url='login')
def createlisting(request):
    # Check if method=POST
    if request.method == "POST":
        # Get form data
        form = CreateForm(request.POST)
        # Check if form data is valid (server-side)
        if form.is_valid():
            # Get all data from the form
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            startingbid = form.cleaned_data["startingbid"]
            category = form.cleaned_data["category"]
            imageURL = form.cleaned_data["imageURL"]
            if not len(imageURL) > 0:
                imageURL = 'https://user-images.githubusercontent.com/52632898/161646398-6d49eca9-267f-4eab-a5a7-6ba6069d21df.png'
            # Save a record
            auctionlisting = AuctionListings(
                user = User.objects.get(pk=request.user.id),
                title = title,
                description = description,
                price = startingbid,
                startingbid = startingbid,
                category = category,
                imageURL = imageURL
            )
            auctionlisting.save()
            # Go back to index
            return redirect(index)
        else:
            # Return filled form if invalid
            return render(request, "auctions/createlisting.html", {
            "form": form
            })
    else:
        # If method=GET, return form
        return render(request, "auctions/createlisting.html", {
            "form": CreateForm()
        })

# Put listing in watchlist for user
@login_required(login_url='login')
def addwatchlist(request,id):
    # Make entry from user and auction to add to watchlist
    entry = Watchlist(
        user = User.objects.get(pk=request.user.id),
        auction = AuctionListings.objects.get(id=id)
        )
    entry.save()
    # Go back to listing page
    return redirect(listing, id)

# Remove listing from watchlist for user
@login_required(login_url='login')
def removewatchlist(request, id):
    # Get user and auction
    user = User.objects.get(pk=request.user.id)
    auction = AuctionListings.objects.get(id=id)
    # Remove entry from watchlist
    entry= Watchlist.objects.get(user=user, auction=auction)
    entry.delete()
    # Go back to listing page
    return redirect(listing, id)

# Make using Django model form
class BidForm(ModelForm):
    amount = forms.DecimalField(label='', required=True, widget=forms.NumberInput(attrs={
                                            'placeholder': 'Bid',
                                            'min': '0.01',
                                            'max': '99999999.99',
                                            'step': '0.01',
                                            'class': 'form-control'
                                        }))
    class Meta:
        model = Bids
        fields = ["amount"]

# Save new bid
@login_required(login_url='login')
def newbid(request, id):
    # Get form data
    form = BidForm(request.POST)
    # Check if form data is valid (server-side)
    if form.is_valid():
        # Get data from the form
        amount = form.cleaned_data["amount"]
        # Get current price and user
        auction = AuctionListings.objects.filter(id=id)
        currentprice = auction.values("price")[0]["price"]
        print(currentprice)
        bidder = User.objects.get(pk=request.user.id)
        print(bidder)
        if not amount > currentprice:
            return HttpResponse("Bid must be higher than current bid!")
        else:
            # Get user and auction
            bid = Bids(
                auction = AuctionListings.objects.get(id=id),
                user = bidder,
                amount = amount
            )
            bid.save()
            # Update current price
            auction.update(price=amount)
    # Go back to listing page
    return redirect(listing, id)

# Make using Django model form
class CommentForm(ModelForm):
    text = forms.CharField(label="", required=True, widget=forms.Textarea(attrs={
                                    'placeholder': "Write a comment",
                                    'aria-label': "description",
                                    "class": "form-control",
                                    'style': 'max-width:500px;max-height:200px',
                                    }))
    class Meta:
        model = Comments
        fields = ["text"]

# Save comment
@login_required(login_url='login')
def comment(request, id):
    # Get form data
    form = CommentForm(request.POST)
    # Check if form data is valid (server-side)
    if form.is_valid():
        # Get data from the form
        text = form.cleaned_data["text"]
        # Save comment
        comment = Comments(
            auction = AuctionListings.objects.get(id=id),
            user = User.objects.get(pk=request.user.id),
            text = text
        )
        comment.save()
    # Go back to listing page
    return redirect(listing, id)

# Close auction
@login_required(login_url='login')
def closeauction(request, id):
    # Set active to False for auction listing
    auction = AuctionListings.objects.filter(id=id)
    auction.update(active=False)
    # Go back to listing page
    return redirect(listing, id)

# Display page of certain listing
def listing(request, id):
    print("id:")
    print(id)
    # Get Model entries using listing id
    auction = AuctionListings.objects.filter(id=id).values()[0]
    print("auction:")
    print(auction)
    #id = int(name)
    bids = Bids.objects.filter(auction=id)
    try:
        winner = bids.values("user").order_by('-amount')[0]["user"]
    except:
        winner = 0
    print("winner:")
    print(winner)
    comments = Comments.objects.filter(auction=id)
    bidder = request.user.id
    # See if listing is in watchlist
    if Watchlist.objects.filter(auction=id, user=bidder).exists():
        watchlist = 1
    else:
        watchlist = 0
    print("watchlist:")
    print(watchlist)
    # Return listing
    return render(request, "auctions/listing.html", {
            "listing": auction,
            "bids": len(bids),
            "winner": winner,
            "comments": comments,
            "bidder": bidder,
            "watchlist": watchlist,
            "bidform": BidForm(),
            "commentform": CommentForm()
        })

# Show all listings in watchlist for user
def displaywatchlist(request):
    # Try to retrieve watchlist for user
    try:
        listings = AuctionListings.objects.filter(watchlist__user = request.user.id).order_by('-datetime')
    # Empty list if user has no watchlist items
    except:
        listings = []
    # Return Watchlist
    return render(request, "auctions/index.html", {
        "title": "Watchlist",
        "listings": listings
    })

# Show all categories and link them with their respective listings
def displaycategories(request):
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })

# Show all listings with certain category
def categoryview(request, cat):
    # Try to retrieve listings with category
    try:
        listings = AuctionListings.objects.filter(category = cat).order_by('-datetime')
    # Empty list if no listings for category
    except:
        listings = []
    # Return Watchlist
    return render(request, "auctions/index.html", {
        "title": "Active listings for "+cat,
        "listings": listings
    })
