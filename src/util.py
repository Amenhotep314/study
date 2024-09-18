"""Contains miscellaneous utility functions that do not deal directlty with the database."""

from flask_login import current_user
from flask_babel import _, lazy_gettext as _l
import datetime
import pytz


"""A note on timezones: These are a nightmare, totally unneccesary for this stage of the process,
but absolutely essential for reliable scalability. Because of this, let's begin the suffering.
Datetimes come from the client, naive and in local time. Immediately make them aware in local time,
then convert to UTC. Datetimes come from the database, unaware and in UTC. Make them aware in UTC.
Perform all operations in UTC. Convert back to local only before sending to the client."""


def current_user_timezone():
    """Gets the current user's timezone.

    Returns:
        A pytz timezone object
    """

    tz_str = current_user.timezone
    return pytz.timezone(tz_str)


def utc_now():
    """Gets the current time in UTC.

    Returns:
        An aware datetime object
    """
    return datetime.datetime.now(tz=pytz.utc)


def local_now():
    """Gets the current user's local time

    Returns:
        An aware datetime object
    """

    utc = utc_now()
    return local_datetime_from_naive_utc_datetime(utc)


def utc_datetime_from_naive_local_date_time(date, time):
    """Gets the current user's timezone.

    Returns:
        A pytz timezone object
    """
    tz = current_user_timezone()
    unaware = datetime.datetime.combine(date, time)
    local = tz.localize(unaware)
    utc = local.astimezone(pytz.utc)

    return utc


def utc_datetime_from_naive_local_date(date, eod=True):
    """Converts an unaware local date to a UTC datetime, either at the end or the beginning of the day.

    Args:
        date: a naive date object
        eod: a boolean indicating whether to return the end of the day. Default True

    Returns:
        A datetime object
    """

    if eod:
        time = datetime.time(23, 59, 59)
    else:
        time = datetime.time(0, 0, 0)

    return utc_datetime_from_naive_local_date_time(date, time)


def utc_datetime_from_naive_utc_datetime(datetime):
    """Converts an unaware UTC datetime to an aware UTC datetime. Useful to call on pretty much any
    datetime object that comes from the database.

    Args:
        datetime: a datetime object

    Returns:
        A datetime object
    """

    try:
        utc = pytz.utc.localize(datetime)
    except:
        utc = datetime

    return utc


def local_datetime_from_naive_utc_datetime(datetime):
    """Converts an unaware UTC datetime to a local datetime.

    Args:
        datetime: a datetime object

    Returns:
        A datetime object
    """

    tz = current_user_timezone()
    utc = utc_datetime_from_naive_utc_datetime(datetime)
    local = utc.astimezone(tz)

    return local


def local_dict_from_naive_utc_query(query):
    """Iterates over a database query response and converts all UTC datetimes to local. Builds a dict
    whose structure mirrors that of the original query. Useful when whole query responses are sent
    to Jinja en masse.

    Args:
        query: An SQLAlchemy query object containing UTC datetime objects

    Returns:
       A dict with the same structure as the query but local datetimes
    """

    query_dict = query.__dict__

    for key in query_dict:
        if isinstance(query_dict[key], datetime.datetime):
            query_dict[key] = local_datetime_from_naive_utc_datetime(query_dict[key])

    return query_dict


def local_dicts_from_naive_utc_queries(queries):
    """Wraps local_dict_from_naive_utc_query for multiple queries.

    Args:
        query: An iterable of SQLAlchemy query objects containing UTC datetime objects

    Returns:
       A list of dicts with the same structures as the queries but local datetimes
    """

    query_dicts = []
    for query in queries:
        query_dicts.append(local_dict_from_naive_utc_query(query))

    return query_dicts


def utc_days_ago(days_ago, eod=False):
    """Gets a UTC datetime object for the start (or end) of a local day a certain number of days ago.
    If it is Thursday for the user, utc_days_ago(1) will return the start of the user's Wednesday in
    UTC. If eod is True, it will return the end of the user's Wednesday.

    Args:
        days_ago: An int representing the number of days to go back from today. Negative values give
        future dates.
        eod: A boolean indicating whether to return the end of the day. Default False

    Returns:
       A datetime object
    """

    date = local_now().date() - datetime.timedelta(days=days_ago)
    return utc_datetime_from_naive_local_date(date, eod=eod)


def social_greeting():
    """Generates a friendly welcome message to display on the home page.

    Returns:
       A str message
    """

    # Address the user by name with a greeting appropriate to the time of day
    user_name = current_user.firstname
    user_datetime = utc_now().astimezone(current_user_timezone())
    user_time = user_datetime.time()
    morning = datetime.time(6, 0)
    afternoon = datetime.time(12, 0)
    evening = datetime.time(18, 0)
    night = datetime.time(23, 59)

    # I'm also thinking of adding some fun seasonal greetings - holidays? That would be a locale problem
    if morning <= user_time < afternoon:
        return _l("Good morning, %(name)s.", name=user_name)
    elif afternoon <= user_time < evening:
        return _l("Good afternoon, %(name)s.", name=user_name)
    elif evening <= user_time < night:
        return _l("Good evening, %(name)s.", name=user_name)
    else:
        return _l("Hello, %(name)s.", name=user_name)


def language_options():
    # Languages with a messages.po file in src/translations. See babel_actions.sh to add more.
    return [
        ("en", "English"),
        ("fr", "Français")
    ]


def theme_options():
    # Possible themes for the user to choose. Matches the names of CSS files in src/static.
    return [
        ("greensboro_winter", _l("Greensboro Winter")),
        ("serenity_now", _l("Serenity Now!")),
    ]


def color_options():
    # Possible course colors and their hex codes. Could always add more here.
    return [
        ("#cf0000", _l("Red")),
        ("#cf8000", _l("Orange")),
        ("#cfcf00", _l("Yellow")),
        ("#00cf00", _l("Green")),
        ("#00cfcf", _l("Cyan")),
        ("#0000cf", _l("Blue")),
        ("#cf00cf", _l("Fuchsia")),
        ("#400080", _l("Purple"))
    ]


def weekdays():
    # The days of the week. There is probably a datetime way for this, but I want to translate them.
    return [
        _l("Monday"),
        _l("Tuesday"),
        _l("Wednesday"),
        _l("Thursday"),
        _l("Friday"),
        _l("Saturday"),
        _l("Sunday")
    ]