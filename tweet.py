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
from pypresence import Presence, Activity


with open("credentials.yaml", "r") as c:
    credentials = yaml.load(c.read(), Loader=yaml.FullLoader)


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

def setup_discord():
    """
    Set up the discord rich presence client
    """
    rpc = Presence(credentials["discord"]["client_id"])
    rpc.connect()
    return rpc

def choose_post(ani_bm_subreddit):
    """
    Choose the post object randomally (while preventing double-posting) and return the object
    """
    # Choose the post out of the 50 hottest posts on the subreddit
    hot = ani_bm_subreddit.hot(limit=50)
    post = random.choice(list(hot))

    # 1. Catching double-posts; 2. Catching long-titled posts
    while post.id in open("already_tweeted.txt").read() or len(post.title) > 265:
        if len(post.title) > 265:
            print("Post title is too long, choosing a different post")
        else:
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


def tweet(twitter_api, ani_bm, discord):
    """
    Tweet 24/7
    """
    # Sleep until next round hour
    now = datetime.datetime.now()
    sleep_until = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    time.sleep((sleep_until - now).seconds)
    while True:
        # Print current hour
        print(datetime.datetime.now().time())

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
            except Exception as e: # Choose a different post if tweeting fails (probably becuase the chosen post does not contain an image)
                if e.args == ("Invalid file type for image: None",):
                    print("Post does not contain an image, choosing a different post")
                else:
                    print(f"Special error - {e.args}")
                post = choose_post(ani_bm)
                post_url = shorten_link(post)
                image_url = post.url
                post_title = post.title

        try: # Trying to update Discord Rich Presence
            discord.update(large_image="large_image", details="Tweeting @ani_bm_bot", state=f"Most recent post: {post_url}")
        except Exception as e:
            print(f"Discord Rich Presence update failed - {e.args}")


        now = datetime.datetime.now()
        sleep_until = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        time.sleep((sleep_until - now).seconds)


def main():
    tweet(setup_twitter(), setup_reddit(), setup_discord())


main()