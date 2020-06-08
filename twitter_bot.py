import csv
import tweepy
import GetOldTweets3 as got

from datetime import date, timedelta
from dotenv import load_dotenv
from os import environ
from time import sleep
from utils import user_props, extract_user_props

load_dotenv()

# store Twitter specific credentials
ACCESS_TOKEN = environ["ACCESS_TOKEN"]
ACCESS_SECRET = environ["ACCESS_SECRET"]
CONSUMER_KEY = environ["CONSUMER_KEY"]
CONSUMER_SECRET = environ["CONSUMER_SECRET"]

ACCOUNT_SCREEN_NAME = environ["ACCOUNT_SCREEN_NAME"]
MAX_UNFOLLOW = 10


class TwitterBot:
    """docstring for TwitterBot"""

    def __init__(self):
        # authorization from values inputted earlier, do not change.
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        self.api = tweepy.API(
            auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
        )

    def _lastSunday(self):
        idx = (date.today().weekday() + 1) % 7
        return date.today() - timedelta(7 + idx)

    def mostRetweetedFromLastWeek(
        self, term="", username=None, min_retweets=0, min_faves=0, near="", lang=""
    ):
        criteria = (
            got.manager.TweetCriteria()
            .setQuerySearch(
                "filter:media -filter:replies min_retweets:%s min_faves:%s %s"
                % (min_retweets, min_faves, term)
            )
            .setSince("{:%Y-%m-%d}".format(self._lastSunday()))
            .setTopTweets(True)
            .setMaxTweets(100)
            .setEmoji("unicode")
        )
        if username:
            criteria.setUsername(username)

        if near:
            criteria.setNear(near)

        if lang:
            criteria.setLang("es")

        return got.manager.TweetManager.getTweets(criteria)

    def build_friends_list(self, output):
        fieldnames = user_props.copy()
        fieldnames.insert(0, "profile_url")
        csvwriter = csv.DictWriter(output, fieldnames=fieldnames)
        csvwriter.writeheader()

        followers_ids = self.api.followers_ids(ACCOUNT_SCREEN_NAME)
        for following in tweepy.Cursor(
            self.api.friends, id=ACCOUNT_SCREEN_NAME
        ).items():
            if following.id in followers_ids:
                csvline = {
                    "profile_url": "https://twitter.com/%s" % following.screen_name
                }
                csvline = extract_user_props(following, csvline)
                print(csvline)
                csvwriter.writerow(csvline)

    def make_unfollowers_list(self):
        with open("data/unfollowers.csv", "w", newline="") as csvfile:
            fieldnames = user_props.copy()
            fieldnames.insert(0, "profile_url")
            csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csvwriter.writeheader()

            followers_ids = self.api.followers_ids(ACCOUNT_SCREEN_NAME)
            for following in tweepy.Cursor(
                self.api.friends, id=ACCOUNT_SCREEN_NAME
            ).items():
                if following.id not in followers_ids:
                    csvline = {
                        "profile_url": "https://twitter.com/%s" % following.screen_name
                    }
                    csvline = extract_user_props(following, csvline)
                    print(csvline)
                    csvwriter.writerow(csvline)

    def unfollow_back_who_not_folow_me(self):
        self.followers = self.api.followers_ids(ACCOUNT_SCREEN_NAME)
        self.following = self.api.friends_ids(ACCOUNT_SCREEN_NAME)
        # function to unfollow users that don't follow you back.
        print("Starting to unfollow users...")
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
                    print(str(total_followed) + " unfollowed so far.")
                if total_followed == self.MAX_UNFOLLOW:
                    print("unfollow %s users now, exiting it" % self.MAX_UNFOLLOW)
                    exit()

                print("Unfollowed user. Sleeping 15 seconds.")
                sleep(15)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                self.error_handling(e)
