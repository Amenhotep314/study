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
            # "plugins": {
            #     "title": {
            #         "display": True,
            #         "text": util.utc_days_ago(days_since_monday).strftime("%Y-%m-%d") + " - " + util.utc_days_ago(days_since_monday + 6).strftime("%Y-%m-%d")
            #     }
            # },
            # "responsive": True,
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


def chart_embed(id, arg):

    return f"""<canvas id="{id}"></canvas><script>renderChart({id}, {arg})</script>"""


