from flask_login import current_user
import datetime
import pytz


"""A note on timezones: These are a nightmare, totally unneccesary for this stage of the process,
but absolutely essential for reliable scalability. Because of this, let's begin the suffering.
Datetimes come from the client, naive and in local time. Immediately make them aware in local time,
then convert to UTC. Datetimes come from the database, unaware and in UTC. Make them aware in UTC.
Perform all operations in UTC. Convert back to local only before sending to the client."""


def current_user_timezone():

    tz_str = current_user.timezone
    return pytz.timezone(tz_str)


def utc_now():

    return datetime.datetime.now(tz=pytz.utc)


def utc_datetime_from_naive_local_date_time(date, time):

    tz = current_user_timezone()
    unaware = datetime.datetime.combine(date, time)
    local = tz.localize(unaware)
    utc = local.astimezone(pytz.utc)

    return utc


def utc_datetime_from_naive_local_date(date, eod=True):

    if eod:
        time = datetime.time(23, 59, 59)
    else:
        time = datetime.time(0, 0, 0)

    return utc_datetime_from_naive_local_date_time(date, time)


def utc_datetime_from_naive_utc_datetime(datetime):

    return pytz.utc.localize(datetime)


def local_datetime_from_naive_utc_datetime(datetime):

    tz = current_user_timezone()
    utc = pytz.utc.localize(datetime)
    local = utc.astimezone(tz)

    return local


def local_dict_from_naive_utc_query(query):

    query_dict = query.__dict__

    for key in query_dict:
        if isinstance(query_dict[key], datetime):
            query_dict[key] = local_datetime_from_naive_utc_datetime(query_dict[key])

    return query_dict


def local_dicts_from_naive_utc_queries(queries):

    query_dicts = []
    for query in queries:
        query_dicts.append(local_dict_from_naive_utc_query(query))

    return query_dicts