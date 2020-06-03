from time import sleep

import tweepy
from dotenv import load_dotenv
from os import environ

load_dotenv()

# store Twitter specific credentials
ACCESS_TOKEN = environ['ACCESS_TOKEN']
ACCESS_SECRET = environ['ACCESS_SECRET']
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']

ACCOUNT_SCREEN_NAME = environ['ACCOUNT_SCREEN_NAME']
MAX_UNFOLLOW = 10

class TwitterBot:
    """docstring for TwitterBot"""
    def __init__(self):
        # authorization from values inputted earlier, do not change.
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        self.api = tweepy.API(auth)
        self.followers = self.api.followers_ids(ACCOUNT_SCREEN_NAME)
        self.following = self.api.friends_ids(ACCOUNT_SCREEN_NAME)
        self.MAX_UNFOLLOW = MAX_UNFOLLOW

    def unfollow_back_who_not_folow_me(self):
        # function to unfollow users that don't follow you back.
        print('Starting to unfollow users...')
        # makes a new list of users who don't follow you back.
        non_mutuals = set(self.following) - set(self.followers)
        total_followed = 0
        for f in non_mutuals:
            try:
                # unfollows non follower.
                print("unfollowing %s" % f)
                self.api.destroy_friendship(f)
                total_followed += 1
                if total_followed % 10 == 0:
                    print(str(total_followed) + ' unfollowed so far.')
                if total_followed==self.MAX_UNFOLLOW:
                    print('unfollow %s users now, exiting it' % self.MAX_UNFOLLOW)
                    exit()

                print('Unfollowed user. Sleeping 15 seconds.')
                sleep(15)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                self.error_handling(e)

        print(total_followed)


if __name__ == '__main__':
    bot = TwitterBot()
    bot.unfollow_back_who_not_folow_me()