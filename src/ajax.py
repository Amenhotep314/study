"""Handles all asynchronous requests from client-side JavaScript."""

from flask import Blueprint, jsonify, abort
from flask_login import login_required
from flask_babel import _, lazy_gettext as _l
from datetime import timedelta

from . import db_util
from . import util

ajax = Blueprint("ajax", __name__)

@login_required
@ajax.route("/weekly_summary/<string:week>", methods=["GET"])
def weekly_summary(week="0"):
    """Builds a bar chart representation of study time by course since Monday.

    Args:
        week: An integer representing the number of weeks after the current week. Default 0

    Returns:
        A JSON object containing the chart configuration.
    """

    # One dataset for every course, each containing a value for every day of the week
    try:
        week = int(week)
    except:
        abort(404)
    datasets = []
    days_since_monday = util.local_now().weekday() - 7 * week   # Find Monday

    for course in db_util.current_courses():
        dataset = {
            "label": course.name,
            "backgroundColor": course.color,
            "data": []
        }
        for i in range(7):
            # Query the db for each weekday, and convert values from seconds to hours
            start_datetime = util.utc_days_ago(days_since_monday - i)
            end_datetime = util.utc_days_ago(days_since_monday - i , eod=True)
            delta = db_util.study_time(start_datetime=start_datetime, end_datetime=end_datetime, courses=[course])
            hours = delta.total_seconds() / 3600
            dataset["data"].append(hours)

        datasets.append(dataset)

    # See Chart.js documentation
    config = {
        "type": "bar",
        "data": {
            "labels": util.weekdays(),
            "datasets": datasets
        },
        "options": {
            "plugins": {
                "title": {
                    "display": True,
                    "text": util.utc_days_ago(days_since_monday).strftime("%Y-%m-%d") + " - " + util.utc_days_ago(days_since_monday - 6).strftime("%Y-%m-%d")
                }
            },
            "responsive": True,
            "maintainAspectRatio": False,
            "scales": {
                "x": {
                    "stacked": True
                },
                "y": {
                    "stacked": True
                }
            }
        }
    }

    return jsonify(config)


@login_required
@ajax.route("/work_distribution/<int:range>", methods=["GET"])
def work_distribution(range=0):
    """Builds a pie chart representation of study time by course.

    Args:
        range: An integer representing the number of past days to include. Default 0, which includes all time.

    Returns:
        A JSON object containing the chart configuration.
    """

    datasets = [
        {
            "label": _l("Study Time"),
            "data": [],
            "backgroundColor": [course.color for course in db_util.current_courses()]
        }
    ]

    for course in db_util.current_courses():
        if range:
            start_datetime = util.utc_days_ago(range)
            delta = db_util.study_time(start_datetime=start_datetime, courses=[course])
            title = _l("Last %(days)s days", days=range)
        else:
            delta = db_util.study_time(courses=[course])
            title = _l("All Time")
        hours = delta.total_seconds() / 3600
        datasets[0]["data"].append(hours)

    config = {
        "type": "doughnut",
        "data": {
            "labels": [course.name for course in db_util.current_courses()],
            "datasets": datasets
        },
        "options": {
            "plugins": {
                "title": {
                    "display": True,
                    "text": title
                },
                "legend": {
                    "position": "top"
                }
            },
            "responsive": True,
            "maintainAspectRatio": True,
        }
    }

    return jsonify(config)


@login_required
@ajax.route("/semester_summary/<int:_>", methods=["GET"])
def semester_summary(_=0):
    """Generate a Chart.js object to visualize study time distribution across the entire semester.

    Returns:
        A JSON object containing the chart configuration.
    """
    semester = db_util.current_semester()
    if semester is None:
        return jsonify("")

    # The semester start and end dates in the user's time
    start_datetime = util.utc_datetime_from_naive_utc_datetime(semester.start_datetime)
    end_datetime = util.utc_datetime_from_naive_utc_datetime(semester.end_datetime)
    now = util.utc_now()

    datasets = []

    for course in db_util.current_courses():
        dataset = {
            "label": course.name,
            "backgroundColor": course.color,
            "data": []
        }
        week_start = start_datetime - timedelta(days=start_datetime.weekday())
        week_end = week_start + timedelta(days=6)
        while week_start <= end_datetime:
            if week_start <= now:
                week_data = db_util.study_time(start_datetime=week_start, end_datetime=week_end, courses=[course])
                week_data = week_data.total_seconds() / 3600
            else:
                week_data = 0

            dataset["data"].append(week_data)
            week_start += timedelta(days=7)
            week_end += timedelta(days=7)

        datasets.append(dataset)

    week_start = start_datetime - timedelta(days=start_datetime.weekday())
    week_starts = [week_start + timedelta(days=i*7) for i in range(len(datasets[0]["data"]))]
    week_labels = [start.strftime("%m-%d") for start in week_starts]

    config = {
        "type": "bar",
        "data": {
            "labels": week_labels,
            "datasets": datasets
        },
        "options": {
            "plugins": {
                "title": {
                    "display": True,
                    "text": semester.name
                }
            },
            "responsive": True,
            "maintainAspectRatio": False,
            "scales": {
                "x": {
                    "stacked": True
                },
                "y": {
                    "stacked": True
                }
            }
        }
    }

    return jsonify(config)



@login_required
@ajax.route("/check_notifications", methods=["GET"])
def check_notifications():
    """Gets the most relevant notification

    Returns:
        A JSON object containing the notification
    """
    relevant_horizon = timedelta(hours=1)
    possible_assignments = db_util.active_assignments()

    if possible_assignments and possible_assignments[0].due_datetime:
        utc_date = util.utc_datetime_from_naive_utc_datetime(possible_assignments[0].due_datetime)
        until_time = utc_date - util.utc_now()

        if until_time < relevant_horizon:
            notification = _l("Assignment <em>%(name)s</em> due in %(time)s minutes", name=possible_assignments[0].name, time=until_time.seconds//60)
            return jsonify(notification)

    relevant_horizon = timedelta(hours=8)
    possible_todos = db_util.active_todos()
    if possible_todos and possible_todos[0].finish_datetime:
        utc_date = util.utc_datetime_from_naive_utc_datetime(possible_todos[0].finish_datetime)
        until_time = utc_date - util.utc_now()

        if until_time < relevant_horizon:
            notification = _l("Todo <em>%(name)s</em> must be done in %(time)s hours", name=possible_todos[0].name, time=until_time.seconds//3600)
            return jsonify(notification)

    return jsonify("")