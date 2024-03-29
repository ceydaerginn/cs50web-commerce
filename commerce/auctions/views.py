from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, listing

def Listing(request, id):
    listingData =Listing.objects.get(pk=id)
    return render(request, "auctions/Listing.html", {
        "Listing": listingData
    })

def index(request):
    activeListings = listing.objects.filter(isActive=True)  # Burada "listing" olarak kullanmalısınız.
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings": activeListings,
        "categories": allCategories,
    })

def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST['category']
        category = Category.objects.get(CategoryName=categoryFromForm)
        activeListings = listing.objects.filter(isActive=True, category=category)
    else:
        activeListings = listing.objects.filter(isActive=True)  # POST değilse, tüm listeleri getir

    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories,
    })
    

def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html",{
            "categories": allCategories
        })
    else:
        # Get data from the form 
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        price= request.POST["price"]
        category = request.POST["category"]
        # Who is the user
        currentUser = request.user

        # Get all content about the particular category
        categoryData = Category.objects.get(CategoryName=category)

        # Create a new listing object
        newListing = listing(
                title=title,
                description=description,
                imageurl=imageurl,  # Burada "imageUrl" değil, "imageurl" kullanın
                price=float(price),
                category=categoryData,
                owner=currentUser
                )
        # Insert the object in our database
        newListing.save()
        # Redirect to index page
        return HttpResponseRedirect(reverse(index))

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
