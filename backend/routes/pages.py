"""
FILE: backend/routes/pages.py
PURPOSE: Serve the static front-end pages (pretty URLs, no template engine needed).
"""
from flask import Blueprint, current_app

pages = Blueprint("pages", __name__)

PAGES = {"": "index.html", "assessment": "assessment.html", "results": "results.html",
         "dashboard": "dashboard.html", "checklist": "checklist.html", "tools": "tools.html"}


def _make(filename):
    def view():
        return current_app.send_static_file(filename)
    view.__name__ = "page_" + filename.replace(".", "_")
    return view


for route, fname in PAGES.items():
    pages.add_url_rule("/" + route, view_func=_make(fname))
