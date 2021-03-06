from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("watching", views.watching, name="watching"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:categoryName>", views.categories_contents, name="categories_contents"),
    
]
