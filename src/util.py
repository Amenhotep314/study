from flask_login import current_user
import datetime
import pytz


def current_user_timezone():

    tz_str = current_user.timezone
    return pytz.timezone(tz_str)


def aware_datetime_from_date_time(date, time):

    tz = current_user_timezone()
    return datetime.datetime.combine(date, time, tzinfo=tz)


def aware_datetime_from_date(date, eod=True):

    tz = current_user_timezone()
    if eod:
        time = datetime.time(23, 59, 59)
    else:
        time = datetime.time(0, 0, 0)
    return datetime.datetime.combine(date, time, tzinfo=tz)