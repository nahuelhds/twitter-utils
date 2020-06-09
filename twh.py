import click
import csv

from twitter_bot import TwitterBot
from utils import extract_got_props, got_props

bot = TwitterBot()


@click.group()
def cli():
    """The twitter helper"""
    pass


@cli.command()
@click.argument("input", type=click.File("r"))
@click.argument("output", type=click.File("w"))
def top(input, output):
    """Get top tweets from the accounts given in the input file and saves them in the output"""

    accounts = input.read().splitlines()

    csvwriter = csv.DictWriter(output, fieldnames=got_props)
    csvwriter.writeheader()

    for tweet in bot.mostRetweetedFromLastWeek(
        username=accounts, lang="es", min_faves=100
    ):
        csvline = extract_got_props(tweet)
        print(csvline)
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
