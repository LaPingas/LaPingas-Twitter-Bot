# Import the Twitter API
import tweepy
# Import the Reddit API
import praw
# Import the bit.ly API
import bitly_api
# Import more useful libraries
import time
import datetime
import random
import requests
import yaml
from io import BytesIO

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
                         client_secret=credentials["twitter"]["client_secret"],
                         username=credentials["twitter"]["username"],
                         password=credentials["twitter"]["password"],
                         user_agent=credentials["twitter"]["user_agent"])
    ani_bm_subreddit = reddit.subreddit("ani_bm")
    return ani_bm_subreddit


def setup_bitly():
    """
    Set up the bit.ly object and return the object
    """
    bitly = bitly_api.Connection(access_token=credentials["bitly"]["api_key"])
    return bitly


def choose_post(ani_bm_subreddit):
    """
    Choose the post object randomally (while preventing double-posting) and return the object
    """
    # Choose the post out of the 20 hottest posts on the subreddit
    hot = ani_bm_subreddit.hot(limit=20)
    post = random.choice(list(hot))

    # Open the double-post prevent file and check whether or not the post has been already posted
    while post.id in open("already_tweeted.txt").read():
        print("Double-post, choosing a different post")
        hot = ani_bm_subreddit.hot(limit=20)
        post = random.choice(list(hot))

    # Write the chosen post to the double-post prevent file
    already_tweeted = open("already_tweeted.txt", "a")
    already_tweeted.write(f"{post}\n")

    # Close the file and return the post
    already_tweeted.close()
    return post


def shorten_link(long_url, bitly):
    """
    Gets the URL to shorten and return the shortened URL
    """
    return bitly.shorten(uri=f"https://reddit.com{long_url}"[:49])["url"]


def setup_current_time():
    """
    Set up the current time in a list form and return the list
    """
    current_time = "{}".format(datetime.datetime.now().time())
    hour = current_time[:2]
    minute = current_time[3:5]
    second = current_time[6:8]
    current_time = [hour, minute, second]
    return current_time


def is_new_hour(current_time):
    """
    Check whether or not it's currently a new hour, return True if it is otherwise False
    """
    return True if current_time[1] == "00" and current_time[2] == "00" else False


def tweet(twitter_api, ani_bm, bitly_api):
    """
    Tweet 24/7
    """
    while True:
        if is_new_hour(setup_current_time()):
            # Print current hour
            print(setup_current_time())

            # Call the post-choosing function
            post = choose_post(ani_bm)
            # Call the URL-shortening function and assign it
            post_url = shorten_link(post.permalink, bitly_api)
            # Assign the image URL
            image_url = post.url

            while True:
                try:  # Try to post
                    twitter_api.update_with_media(file=BytesIO(requests.get(image_url).content),
                                                  filename=image_url.split('/')[-1].split('#')[0].split('?')[0],
                                                  status=f"אני_במציאות {post_url}")
                    print("Posted")
                    break
                except Exception:  # Choose a different post if it fails (probably becuase the chosen post does not contain an image)
                    print("Post does not contain an image, choosing a different post")
                    post = choose_post(setup_reddit())
                    post_url = shorten_link(post.permalink, bitly_api)
                    image_url = post.url

            # Sleep for almost an hour
            time.sleep(3555)
            # Return to constant hour check for the rest of the hour

        # Sleep a second after every check
        time.sleep(1)


def main():
    tweet(setup_twitter(), setup_reddit(), setup_bitly())


main()
