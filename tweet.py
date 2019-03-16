# Import the Twitter app keys
from keys import *
# Import the Twitter API
import tweepy
# Import more useful libraries
import time
import datetime
from random import randint

def setup_api():
    """
    Set up the neccessary authorization keys and API object
    :rtype: Object
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

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

def tweet(api):
    """
    Tweet
    :param api: The Twitter API object
    :type api: Object
    """
    while True:
        if is_new_hour(setup_current_time()):
            random_number = randint(1, 1001)
            print("{0}:{1} - {2}".format(setup_current_time()[0], setup_current_time()[1], random_number))
            api.update_status(random_number)
            time.sleep(1)

def main():
    tweet(setup_api())

main()