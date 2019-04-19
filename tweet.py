# Import the Twitter API
import tweepy
# Import the Reddit API
import praw
# Import more useful libraries
import time
import datetime
import random
import requests
from io import BytesIO
import yaml

with open("credentials.yaml", "r") as f:
    credentials = yaml.load(f.read())


def setup_twitter():
    """
    Set up the Twitter object and return the object
    """
    auth = tweepy.OAuthHandler(credentials["twitter"]["consumer_key"], credentials["twitter"]["consumer_secret"])
    auth.set_access_token(credentials["twitter"]["access_token"], credentials["twitter"]["access_token_secret"])
    return tweepy.API(auth)


def setup_reddit():
    """
    Set up the subreddit object and return the object
    """
    reddit = praw.Reddit(client_id=credentials["reddit"]["client_id"],
                         client_secret=credentials["reddit"]["client_secret"],
                         username=credentials["reddit"]["username"],
                         password=credentials["reddit"]["password"],
                         user_agent=credentials["reddit"]["user_agent"])
    ani_bm_subreddit = reddit.subreddit("ani_bm")
    return ani_bm_subreddit


def choose_post(ani_bm_subreddit):
    """
    Choose the post object randomally (while preventing double-posting) and return the object
    """
    # Choose the post out of the 50 hottest posts on the subreddit
    hot = ani_bm_subreddit.hot(limit=50)
    post = random.choice(list(hot))

    # Open the double-post prevent file and check whether or not the post has been already posted
    while post.id in open("already_tweeted.txt").read():
        print("Double-post, choosing a different post")
        hot = ani_bm_subreddit.hot(limit=50)
        post = random.choice(list(hot))

    # Write the chosen post to the double-post prevent file
    already_tweeted = open("already_tweeted.txt", "a")
    already_tweeted.write(f"{post}\n")
    
    # Close the file and return the post
    already_tweeted.close()
    return post


def shorten_link(post):
    """
    Gets the URL to shorten and return the shortened URL
    """
    return f"redd.it/{post.id}"


def tweet(twitter_api, ani_bm):
    """
    Tweet 24/7
    """
    # Sleep until next round hour
    now = datetime.datetime.now()
    sleep_until = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    time.sleep((sleep_until - now).seconds)
    while True:
        # Print current hour
        print(now.isoformat())

        # Call the post-choosing function
        post = choose_post(ani_bm)
        # Call the URL-shortening function and assign it
        post_url = shorten_link(post)
        # Assign the image URL
        image_url = post.url
        # Assign the post title
        post_title = post.title

        while True:
            try: # Try to post
                twitter_api.update_with_media(file = BytesIO(requests.get(image_url).content),
                                              filename = image_url.split('/')[-1].split('#')[0].split('?')[0],
                                              status = f"{post_title} {post_url}")
                print("Posted")
                break
            except Exception: # Choose a different post if it fails (probably becuase the chosen post does not contain an image)
                print("Post does not contain an image, choosing a different post")
                post = choose_post(setup_reddit())
                post_url = shorten_link(post)
                image_url = post.url

        now = datetime.datetime.now()
        sleep_until = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        time.sleep((sleep_until - now).seconds)


def main():
    tweet(setup_twitter(), setup_reddit())


main()