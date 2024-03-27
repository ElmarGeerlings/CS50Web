from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("addwatchlist/<int:id>", views.addwatchlist, name="addwatchlist"),
    path("removewatchlist/<int:id>", views.removewatchlist, name="removewatchlist"),
    path("newbid/<int:id>", views.newbid, name="newbid"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("closeauction/<int:id>", views.closeauction, name="closeauction"),
    path("displaywatchlist", views.displaywatchlist, name="displaywatchlist"),
    path("displaycategories", views.displaycategories, name="displaycategories"),
    path("categoryview/<str:cat>", views.categoryview, name="categoryview")
]
