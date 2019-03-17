# Import secret credentials
from credentials import *
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
from io import BytesIO

def setup_twitter():
    """
    Set up the Twitter object
    :rtype: Object
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

def setup_reddit():
    """
    Set up the Reddit object
    :rtype: Object
    """
    reddit = praw.Reddit(client_id = hidden_client_id, client_secret = hidden_client_secret, username = hidden_username, password = hidden_password, user_agent = hidden_user_agent)
    ani_bm_subreddit = reddit.subreddit("ani_bm")
    return ani_bm_subreddit

def setup_bitly():
    """
    Set up the bit.ly object
    :rtype: Object
    """
    bitly = bitly_api.Connection(access_token = api_key)
    return bitly

def choose_post(ani_bm_subreddit):
    print(setup_current_time())

    print("Choosing a post")
    hot = ani_bm_subreddit.hot(limit = 20)
    post = random.choice(list(hot))

    print("Opening and checking file")
    already_tweeted = open("already_tweeted.txt", "r")
    already_tweeted_posts = already_tweeted.readlines()
    while post in already_tweeted_posts:
        print("Choosing a different post")
        post = random.choice(list(hot))
    already_tweeted.close()
    already_tweeted = open("already_tweeted.txt", "a")

    print("Writing to file")
    already_tweeted.write("{}\n".format(post))
    
    print("Done! Returning to tweeting...")
    already_tweeted.close()
    return post

def shorten_link(long_url, bitly):
    return bitly.shorten(uri = f"https://reddit.com{long_url}"[:49])["url"]

def setup_current_time():
    """
    Set up the current time in a list form
    :rtype: List
    """
    current_time = "{}".format(datetime.datetime.now().time())
    hour = current_time[:2]
    minute = current_time[3:5]
    second = current_time[6:8]
    current_time = [hour, minute, second]
    return current_time

def is_new_hour(current_time):
    """
    Checks if it's a new hour
    :param current_time: Represent the current time
    :type current_time: List
    """
    return True if current_time[1] == "00" and current_time[2] == "00" else False

def tweet(twitter_api, reddit_api, bitly_api):
    """
    Tweet
    :param api: The Twitter API object
    :type api: Object
    """
    while True:
        if is_new_hour(setup_current_time()):
            while True:
                post = choose_post(setup_reddit())
                post_url = post.permalink
                image_url = post.url
                post_url = shorten_link(post_url, bitly_api)
                twitter_api.update_with_media(file = BytesIO(requests.get(image_url).content), filename = image_url.split('/')[-1].split('#')[0].split('?')[0], status = "אני_במציאות {}".format(post_url))
                time.sleep(3555)
                break
        time.sleep(1)

def main():
    tweet(setup_twitter(), setup_reddit(), setup_bitly())

main()