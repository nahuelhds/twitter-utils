import click
import csv
import sys

from twitter_bot import TwitterBot
from utils import extract_got_props, got_props

bot = TwitterBot()


@click.group()
def cli():
    """The twitter helper"""
    pass


@cli.command()
@click.argument("username")
@click.argument("output", type=click.File("w"))
def tweets(username, output):
    """Get top tweets from the accounts given in the input file and saves them in the output"""

    csvwriter = csv.DictWriter(output, fieldnames=got_props)
    csvwriter.writeheader()
    for tweet in bot.allTweets(username):
        csvline = extract_got_props(tweet)
        print(csvline)
        csvwriter.writerow(csvline)


@cli.command()
@click.argument("output", type=click.File("a"))
@click.argument("since")
@click.argument("until")
def my_tweets(output, since, until):
    """Get top tweets from the accounts given in the input file and saves them in the output"""

    csvwriter = csv.DictWriter(output, fieldnames=got_props)
    for tweet in bot.myTweets(since, until):
        csvline = extract_got_props(tweet)
        print(csvline)
        csvwriter.writerow(csvline)


@cli.command()
@click.argument("output", type=click.File("w"))
@click.option("-u", "--usernames", type=click.File("r"), default="-")
@click.option("--rts", default=0)
@click.option("--favs", default=0)
@click.option("--lang", default="")
@click.option("--near")
def top_media(output, usernames, near, rts, favs, lang):
    """Get top tweets from the accounts given in the input file and saves them in the output"""

    accounts = usernames.read().splitlines()

    csvwriter = csv.DictWriter(output, fieldnames=got_props)
    csvwriter.writeheader()

    for tweet in bot.topMediaToday(
        usernames=accounts, lang=lang, min_retweets=rts, min_faves=favs, near=near
    ):
        csvline = extract_got_props(tweet)
        click.echo(
            "%s = %s - rts: %s, favs: %s"
            % (tweet.date, tweet.permalink, tweet.retweets, tweet.favorites)
        )
        csvwriter.writerow(csvline)


@cli.command()
@click.argument("output", type=click.File("w"))
def friends(output):
    """Creates a friends list based on your friends"""
    bot.build_friends_list(output)


@cli.command()
@click.argument("output", type=click.File("w"))
def unfollowers(output):
    """Creates a unfollowers list based on your friends"""
    bot.build_unfollowers_list(output)


@cli.command()
@click.argument("input", type=click.File("r"))
def unfollow_back(input):
    """Follows back based on the input file"""
    bot.unfollow_back(input)


@cli.command()
def auth():
    """Provides auth url for grant permissions for your account"""
    bot.auth()


@cli.command()
def tweets2feed():
    """Monitor best tweets from the defined accounts and generates an RSS/Atom feed"""
    bot.myTweets()


if __name__ == "__main__":
    tweets2feed(sys.argv[1:])
