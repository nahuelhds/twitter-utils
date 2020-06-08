user_props = [
    "id",
    "id_str",
    "name",
    "screen_name",
    "location",
    "description",
    "url",
    "protected",
    "followers_count",
    "friends_count",
    "listed_count",
    "created_at",
    "favourites_count",
    "utc_offset",
    "time_zone",
    "geo_enabled",
    "verified",
    "statuses_count",
    "lang",
    "contributors_enabled",
    "is_translator",
    "is_translation_enabled",
    "profile_background_color",
    "profile_background_image_url",
    "profile_background_image_url_https",
    "profile_background_tile",
    "profile_image_url",
    "profile_image_url_https",
    "profile_banner_url",
    "profile_link_color",
    "profile_sidebar_border_color",
    "profile_sidebar_fill_color",
    "profile_text_color",
    "profile_use_background_image",
    "has_extended_profile",
    "default_profile",
    "default_profile_image",
    "following",
    "follow_request_sent",
    "notifications",
    "translator_type",
]


def extract_user_props(user, parsed_user={}):
    for prop in user_props:
        try:
            parsed_user[prop] = getattr(user, prop) or ""
        except AttributeError:
            print("Could not read property %s from user" % prop)
    return parsed_user


got_props = [
    "id",
    "permalink",
    "username",
    "to",
    "text",
    "date",
    "retweets",
    "favorites",
    "mentions",
    "hashtags",
    "geo",
]


def extract_got_props(tweet, parsed_tweet={}):
    for prop in got_props:
        try:
            parsed_tweet[prop] = getattr(tweet, prop) or ""
        except AttributeError:
            print("Could not read property %s from tweet" % prop)
    return parsed_tweet
