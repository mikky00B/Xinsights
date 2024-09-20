from django.db import models
from django.contrib.auth.models import User


class TwitterUserData(models.Model):
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    followers_count = models.IntegerField()
    following_count = models.IntegerField()
    tweet_count = models.IntegerField()
    listed_count = models.IntegerField()

    # New fields for engagement metrics
    likes_count = models.IntegerField(default=0)
    retweets_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Twitter User Data"
        verbose_name_plural = "Twitter Users Data"


# Create your models here.
class FollowerCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)


class TwitterTweet(models.Model):
    user = models.ForeignKey(TwitterUserData, on_delete=models.CASCADE)
    tweet_id = models.CharField(max_length=255, unique=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)
    retweets_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Tweet by {self.user.username}: {self.text[:20]}"
