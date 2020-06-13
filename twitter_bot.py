import csv

import click
import tweepy
import GetOldTweets3 as got

from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from os import environ
from time import sleep
from utils import user_props, extract_user_props

load_dotenv()

# store Twitter specific credentials
ACCESS_TOKEN = environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = environ["ACCESS_TOKEN_SECRET"]
CONSUMER_KEY = environ["CONSUMER_KEY"]
CONSUMER_SECRET = environ["CONSUMER_SECRET"]
ACCOUNT_SCREEN_NAME = environ["ACCOUNT_SCREEN_NAME"]


class TwitterBot:
    """docstring for TwitterBot"""

    def get_api(self):
        # authorization from values inputted earlier, do not change.
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def topTweets(self, usernames, since=None, until=None):
        return self.buildCriteria(usernames, since, until, True)

    def allTweets(self, usernames):
        return self.buildCriteria(usernames)

    def myTweets(self, since=None, until=None):
        return self.buildCriteria(ACCOUNT_SCREEN_NAME, since, until)

    def buildCriteria(self, usernames, since=None, until=None, topTweets=False):
        criteria = (
            got.manager.TweetCriteria()
            .setUsername(usernames)
            .setTopTweets(topTweets)
            .setSince(since)
            .setUntil(until)
            .setEmoji("unicode")
        )
        return got.manager.TweetManager.getTweets(criteria)

    def topMediaToday(
        self,
        query="",
        usernames=None,
        min_retweets=0,
        min_faves=0,
        near=None,
        lang=None,
    ):
        fromUsernames = (
            usernames if type(usernames) == "str" else " OR from:".join(usernames)
        )
        querysearch = (
            "(from:%s) filter:media -filter:replies min_retweets:%s min_faves:%s %s"
            % (fromUsernames, min_retweets, min_faves, query,)
        )
        since = "{:%Y-%m-%d}".format(date.today() - timedelta(days=1))

        criteria = (
            got.manager.TweetCriteria()
            .setSince(since)
            .setQuerySearch(querysearch)
            .setTopTweets(True)
            .setEmoji("unicode")
        )

        click.echo("CRITERIA")
        click.echo("usernames: %s" % usernames)
        click.echo("querysearch: %s" % querysearch)
        click.echo("since: %s" % since)
        click.echo("near: %s" % near)
        click.echo("lang: %s" % lang)

        return got.manager.TweetManager.getTweets(criteria)

    def build_friends_list(self, output):
        fieldnames = user_props.copy()
        fieldnames.insert(0, "profile_url")
        fieldnames.insert(0, "checked_at")
        csvwriter = csv.DictWriter(output, fieldnames=fieldnames)
        csvwriter.writeheader()

        now = datetime.now()

        api = self.get_api()
        followers_ids = api.followers_ids(ACCOUNT_SCREEN_NAME)
        for following in tweepy.Cursor(api.friends, id=ACCOUNT_SCREEN_NAME).items():
            if following.id in followers_ids:
                csvline = {
                    "checked_at": "{:%Y-%m-%d %H:%M:%S}".format(now),
                    "profile_url": "https://twitter.com/%s" % following.screen_name,
                }
                csvline = extract_user_props(following, csvline)
                print(following.screen_name)
                csvwriter.writerow(csvline)

    def build_unfollowers_list(self, output):
        fieldnames = user_props.copy()
        fieldnames.insert(0, "profile_url")
        fieldnames.insert(0, "checked_at")
        csvwriter = csv.DictWriter(output, fieldnames=fieldnames)
        csvwriter.writeheader()

        now = datetime.now()

        api = self.get_api()
        followers_ids = api.followers_ids(ACCOUNT_SCREEN_NAME)
        for following in tweepy.Cursor(api.friends, id=ACCOUNT_SCREEN_NAME).items():
            if following.id not in followers_ids:
                csvline = {
                    "checked_at": "{:%Y-%m-%d %H:%M:%S}".format(now),
                    "profile_url": "https://twitter.com/%s" % following.screen_name,
                }
                csvline = extract_user_props(following, csvline)
                print(following.screen_name)
                csvwriter.writerow(csvline)

    def unfollow_back(self, input, max_unfollow=100):
        csvreader = csv.DictReader(input)
        unfollowed_count = 0

        api = self.get_api()
        for user in csvreader:

            if user["unfollow"]:
                print("unfollowing %s" % user["screen_name"])
                try:
                    api.destroy_friendship(user["id_str"])
                except Exception as e:
                    print(
                        "Exiting because an unknown error ocrurred. Reason: %s" % str(e)
                    )
                    exit()

                unfollowed_count += 1

                if unfollowed_count % 10 == 0:
                    print(str(unfollowed_count) + " unfollowed so far.")

                if unfollowed_count == max_unfollow:
                    print("unfollow %s users now. Exiting." % max_unfollow)
                    exit()

                print("Sleeping 10 seconds.")
                sleep(10)

    def auth(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.secure = True
        auth_url = auth.get_authorization_url()
        input(
            "Log in to https://twitter.com as the user you want to tweet as and hit enter."
        )
        input("Visit %s in your browser and hit enter." % auth_url)
        pin = input("What is your PIN: ")

        token = auth.get_access_token(verifier=pin)
        print(
            "\nThese are your access token and secret.\nDO NOT SHARE THEM WITH ANYONE!\n"
        )
        print("ACCESS_TOKEN=%s\n" % token[0])
        print("ACCESS_TOKEN_SECRET=%s\n" % token[1])
