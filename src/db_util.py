from flask_login import current_user
from datetime import date
from functools import cache

from . import db
from .models import *


@cache
def current_semester():

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    if not semesters:
        return None

    now = date.today().toordinal()
    semesters.sort(reverse=True, key = lambda x: x.end_date.toordinal())
    for semester in semesters:
        if semester.start_date.toordinal() <= now <= semester.end_date.toordinal():
            return semester

    return semesters[0]


def invalidate_caches():

    cached_funcs = [
        current_semester
    ]

    for func in cached_funcs:
        func.cache_clear()