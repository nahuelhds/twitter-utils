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
def friends_list(output):
    """Creates a file based on your friends"""
    bot.build_friends_list(output)
