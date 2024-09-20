from celery import shared_task
from .models import TwitterUserData, TwitterTweet
from .utils import get_twitter_client
import tweepy


@shared_task
def fetch_and_store_tweet_metrics(user_id):
    from django.contrib.auth.models import User

    user = User.objects.get(id=user_id)
    client = get_twitter_client()
    if client is not None:
        user = client.get_user(username="Sir_Cleverr", user_fields=["public_metrics"])
        tweets = client.user_timeline(screen_name="your_twitter_handle", count=10)
        for tweet in tweets:
            TweetMetrics.objects.create(
                user=user,
                tweet_id=tweet.id_str,
                likes=tweet.favorite_count,
                retweets=tweet.retweet_count,
                mentions=len(tweet.entities["user_mentions"]),
            )


@shared_task(bind=True, max_retries=5)
def fetch_twitter_data(self, username):
    print(f"Starting task for username: {username}")  # Log when the task starts

    try:
        # Set up the Twitter API client
        client = get_twitter_client()

        # Check if the username is None or empty
        if not username:
            raise ValueError("Username cannot be empty.")

        # Fetch user data by username
        user = client.get_user(usernames=[username], user_fields=["public_metrics"])
        print(
            f"Twitter API call result for {username}: {user}"
        )  # Log the raw API response

        if user and user.data:
            user_data = user.data[0]
            metrics = user_data["public_metrics"]
            name = user_data["name"]

            print(
                f"Fetched Data for {username}: Name: {name}, Followers: {metrics['followers_count']}"
            )

            # Update the database
            TwitterUserData.objects.update_or_create(
                username=username,
                defaults={
                    "name": name,
                    "followers_count": metrics["followers_count"],
                    "following_count": metrics["following_count"],
                    "tweet_count": metrics["tweet_count"],
                    "listed_count": metrics["listed_count"],
                },
            )
            print(f"Successfully updated data for {username}")
            return f"Successfully fetched and updated data for {username}."
        else:
            print(f"No data found for {username}")
            return "User data not found."

    except tweepy.TweepyException as e:
        print(f"Twitter API error: {e}")
        self.retry(exc=e, countdown=60 * 2)  # Retry in case of Twitter API errors

    except Exception as e:
        print(f"General error: {e}")
        return f"Failed to fetch data: {str(e)}"


@shared_task(bind=True)
def fetch_recent_tweets(username):
    try:
        client = get_twitter_client()
        user = client.get_user(usernames=[username])

        if user and user.data:
            user_id = user.data[0].id
            tweets = client.get_users_tweets(user_id, tweet_fields=["public_metrics"])

            for tweet in tweets.data:
                # Update or create a tweet record
                TwitterTweet.objects.update_or_create(
                    tweet_id=tweet.id,
                    defaults={
                        "user": TwitterUserData.objects.get(username=username),
                        "text": tweet.text,
                        "likes_count": tweet.public_metrics["like_count"],
                        "retweets_count": tweet.public_metrics["retweet_count"],
                        "replies_count": tweet.public_metrics["reply_count"],
                    },
                )
            return "Successfully fetched and updated recent tweets."
        else:
            return "User data not found."

    except tweepy.TweepyException as e:
        print(f"Error fetching tweets: {e}")
        self.retry(exc=e, countdown=60)

    except Exception as e:
        print(f"General error: {e}")
        return f"Failed to fetch tweets: {str(e)}"


@shared_task(bind=True)
def like_recent_tweets(username):
    try:
        client = get_twitter_client()
        user = client.get_user(usernames=[username])

        if user and user.data:
            user_id = user.data[0].id
            tweets = client.get_users_tweets(user_id)

            for tweet in tweets.data:
                client.like(tweet.id)
                print(f"Liked tweet: {tweet.id}")

            return "Successfully liked recent tweets."
        else:
            return "User data not found."

    except tweepy.TweepyException as e:
        print(f"Error liking tweets: {e}")
        self.retry(exc=e, countdown=60)

    except Exception as e:
        print(f"General error: {e}")
        return f"Failed to like tweets: {str(e)}"


@shared_task(bind=True)
def retweet_recent_tweets(username):
    try:
        client = get_twitter_client()
        user = client.get_user(usernames=[username])

        if user and user.data:
            user_id = user.data[0].id
            tweets = client.get_users_tweets(user_id)

            for tweet in tweets.data:
                client.retweet(tweet.id)
                print(f"Retweeted tweet: {tweet.id}")

            return "Successfully retweeted recent tweets."
        else:
            return "User data not found."

    except tweepy.TweepyException as e:
        print(f"Error retweeting: {e}")
        self.retry(exc=e, countdown=60)

    except Exception as e:
        print(f"General error: {e}")
        return f"Failed to retweet: {str(e)}"


@shared_task(bind=True)
def reply_to_recent_mentions(username, reply_text):
    try:
        client = get_twitter_client()
        user = client.get_user(usernames=[username])

        if user and user.data:
            user_id = user.data[0].id
            mentions = client.get_users_mentions(user_id)

            for mention in mentions.data:
                client.reply(mention.id, reply_text)
                print(f"Replied to mention: {mention.id}")

            return "Successfully replied to recent mentions."
        else:
            return "User data not found."

    except tweepy.TweepyException as e:
        print(f"Error replying to mentions: {e}")
        self.retry(exc=e, countdown=60)

    except Exception as e:
        print(f"General error: {e}")
        return f"Failed to reply to mentions: {str(e)}"
