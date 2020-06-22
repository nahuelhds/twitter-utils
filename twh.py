import click
import csv
import socketserver
import sys

from dotenv import load_dotenv
from feedgen.feed import FeedGenerator
from http.server import SimpleHTTPRequestHandler
from os import environ
from pyngrok import ngrok
from twitter_bot import TwitterBot
from utils import extract_got_props, got_props

load_dotenv()

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
def expose():
    """Go live"""
    port = 8443
    public_url = ngrok.connect(port)
    click.echo(public_url)
    run_server(port)


class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/rss.xml"

        if self.path == "/rss.xml" or self.path == "/atom.xml":
            return SimpleHTTPRequestHandler.do_GET(self)

        return None


def run_server(port=8080):

    # Create an object of the above class
    with socketserver.TCPServer(("", port), MyHttpRequestHandler) as httpd:
        print("serving at port", port)
        httpd.serve_forever()


@cli.command()
def tweets2feed():
    """Monitor best tweets from the defined accounts and generates an RSS/Atom feed"""
    with open("data/accounts.txt") as file:
        accounts = file.read().splitlines()

        feed = init_feed()

        for tweet in bot.topMediaToday(usernames=accounts):
            click.echo(
                "%s = %s - rts: %s, favs: %s"
                % (tweet.date, tweet.permalink, tweet.retweets, tweet.favorites,)
            )
            entry = feed.add_entry()
            entry.id(tweet.id)
            entry.title(tweet.text)
            entry.description("")
            entry.content("")
            entry.link(href=tweet.permalink)
            entry.updated(tweet.date)

        feed.rss_file("rss.xml", pretty=True)
        feed.rss_file("atom.xml", pretty=True)


def init_feed():

    id = environ["FEED_ID"]
    title = environ["FEED_TITLE"]
    subtitle = environ["FEED_SUBTITLE"]
    language = environ["FEED_LANGUAGE"]
    link = environ["FEED_LINK"]
    link_alternate = environ["FEED_LINK_ALTERNATE"]
    logo = environ["FEED_LOGO"]
    author_name = environ["FEED_AUTHOR_NAME"]
    author_email = environ["FEED_AUTHOR_EMAIL"]

    fg = FeedGenerator()
    fg.id(id)
    fg.title(title)
    fg.subtitle(subtitle)
    fg.language(language)
    fg.link(href=link, rel="self")
    fg.link(href=link_alternate, rel="alternate")
    fg.logo(logo)
    fg.author({"name": author_name, "email": author_email})

    return fg


if __name__ == "__main__":
    tweets2feed(sys.argv[1:])
