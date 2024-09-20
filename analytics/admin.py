from django.contrib import admin
from .models import FollowerCount, TwitterUserData

# Register your models here.
admin.site.register(FollowerCount)
admin.site.register(TwitterUserData)
