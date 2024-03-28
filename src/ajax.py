from flask import Blueprint, jsonify
from flask_login import login_required
from flask_babel import _, lazy_gettext as _l

from . import db_util
from . import util

ajax = Blueprint("ajax", __name__)

@login_required
@ajax.route("/weekly_summary/<int:week>", methods=["GET"])
def weekly_summary(week=0):

    datasets = []
    days_since_monday = util.local_now().weekday() + 7 * week

    for course in db_util.current_courses():
        dataset = {
            "label": course.name,
            "backgroundColor": course.color,
            "data": []
        }
        for i in range(7):
            start_datetime = util.utc_days_ago(days_since_monday - i)
            end_datetime = util.utc_days_ago(days_since_monday - i , eod=True)
            delta = db_util.study_time(start_datetime=start_datetime, end_datetime=end_datetime, courses=[course])
            hours = delta.total_seconds() / 3600
            dataset["data"].append(hours)

        datasets.append(dataset)

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



