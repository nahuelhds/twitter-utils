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

def extract_user_props(user, dict = {}):
    for prop in user_props:
        try:
            dict[prop] = getattr(user, prop) or ''
        except AttributeError:
            print("Could not read property %s from user" % prop)
    return dict