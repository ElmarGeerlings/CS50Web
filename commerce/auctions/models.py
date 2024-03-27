from django.contrib.auth.models import AbstractUser
from django.db import models

# User model inhereted from Django
class User(AbstractUser):
    pass

# Contains all info about an auction listing
class AuctionListings(models.Model):
    # Model fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    startingbid = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    category = models.CharField(max_length=100)
    imageURL = models.URLField(blank=True)
    #imageURL = models.URLField(default='https://user-images.githubusercontent.com/52632898/161646398-6d49eca9-267f-4eab-a5a7-6ba6069d21df.png')
    #bid_counter = models.IntegerField(default=1)
    datetime = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "auction"
        verbose_name_plural = "auctions"

    def __str__(self):
        return f'{self.title}: by {self.user.username}'

# Contains all info about a certain bid
class Bids(models.Model):
    # Model fields
    auction = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "bid"
        verbose_name_plural = "bids"

    def __str__(self):
        return f'{self.amount} on {self.auction} by {self.user.username}'

# Comments on listings
class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

    def __str__(self):
        return f"Comment {self.id} on auction {self.auction} made by {self.user}"


# Watchlist
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    auction = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "watchlist"
        verbose_name_plural = "watchlists"
        # Forces to not have auction duplicates for one user
        unique_together = ["auction", "user"]

    def __str__(self):
        return f"{self.auction} on user {self.user} watchlist"
