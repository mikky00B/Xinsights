from django.conf import settings
import matplotlib.pyplot as plt
import tweepy
from django.core.mail import send_mail
from .models import TwitterTweet, TwitterUserData


def get_twitter_client():
    auth = tweepy.OAuthHandler(settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET)
    auth.set_access_token(
        settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET
    )
    client = tweepy.API(auth)
    client = tweepy.Client(bearer_token=settings.BEARER_TOKEN)
    print(client)
    # client = tweepy.Client(bearer_token=settings.BEARER_TOKEN)
    return client


def analyze_engagement(username):
    try:
        user_data = TwitterUserData.objects.get(username=username)
        tweets = TwitterTweet.objects.filter(user=user_data)

        total_likes = sum(tweet.likes_count for tweet in tweets)
        total_retweets = sum(tweet.retweets_count for tweet in tweets)
        total_replies = sum(tweet.replies_count for tweet in tweets)

        total_engagements = total_likes + total_retweets + total_replies
        tweet_count = tweets.count()

        engagement_rate = (
            (total_engagements / user_data.followers_count * 100)
            if user_data.followers_count
            else 0
        )
        average_engagement_per_tweet = (
            (total_engagements / tweet_count) if tweet_count else 0
        )

        # Print or log the analysis
        print(f"Engagement analysis for {username}:")
        print(f"Total Likes: {total_likes}")
        print(f"Total Retweets: {total_retweets}")
        print(f"Total Replies: {total_replies}")
        print(f"Total Engagements: {total_engagements}")
        print(f"Engagement Rate: {engagement_rate:.2f}%")
        print(f"Average Engagement per Tweet: {average_engagement_per_tweet:.2f}")

        return {
            "total_likes": total_likes,
            "total_retweets": total_retweets,
            "total_replies": total_replies,
            "total_engagements": total_engagements,
            "engagement_rate": engagement_rate,
            "average_engagement_per_tweet": average_engagement_per_tweet,
        }

    except TwitterUserData.DoesNotExist:
        print(f"No data found for user: {username}")
        return None
    except Exception as e:
        print(f"Error during analysis: {e}")
        return None


def visualize_engagement(username, engagement_data):
    metrics = ["Total Likes", "Total Retweets", "Total Replies"]
    values = [
        engagement_data["total_likes"],
        engagement_data["total_retweets"],
        engagement_data["total_replies"],
    ]

    plt.bar(metrics, values)
    plt.title(f"Engagement Metrics for {username}")
    plt.ylabel("Counts")
    plt.show()


def generate_engagement_report(username):
    try:
        user_data = TwitterUserData.objects.get(username=username)
        engagement_data = analyze_engagement(username)

        report = {
            "username": username,
            "followers_count": user_data.followers_count,
            "total_likes": engagement_data["total_likes"],
            "total_retweets": engagement_data["total_retweets"],
            "total_replies": engagement_data["total_replies"],
            "engagement_rate": engagement_data["engagement_rate"],
            "average_engagement_per_tweet": engagement_data[
                "average_engagement_per_tweet"
            ],
        }

        print("Engagement Report:")
        for key, value in report.items():
            print(f"{key}: {value}")

        return report

    except TwitterUserData.DoesNotExist:
        print(f"No data found for user: {username}")
        return None


def send_engagement_report(username, report):
    subject = f"Engagement Report for {username}"
    message = "\n".join([f"{key}: {value}" for key, value in report.items()])
    recipient_list = ["recipient@example.com"]  # Change to actual recipient
    send_mail(subject, message, "your_email@example.com", recipient_list)
