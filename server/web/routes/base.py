import functools

from flask import flash, redirect, render_template, request, url_for
import requests

from ..auth import auth


def flash_success(msg):
    flash(msg, "success")


def flash_error(msg):
    flash(msg, "error")


def redirect_url(default="home"):
    return request.args.get("next") or request.referrer or url_for(default)


def redirect_prev(anchor=None):
    url = redirect_url()
    if anchor is not None:
        url += f"#{anchor}"
    return redirect(url)


def arduino_get_route(f):
    @auth.login_required
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            logs = f"GET {e.request.url}"
            return render_template("arduino_404.html", logs=logs), 500

    functools.update_wrapper(decorated, f)
    return decorated


def arduino_post_route(func):
    @auth.login_required
    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            req_logs = f"POST {e.request.url} {e.request.body}"
            resp_logs = e.response.text
            return (
                render_template("arduino_400.html", req=req_logs, resp=resp_logs),
                500,
            )
        except requests.exceptions.RequestException as e:
            req_logs = f"POST {e.request.url} {e.request.body}"
            return render_template("arduino_404.html", logs=req_logs), 500

    functools.update_wrapper(decorated, func)
    return decorated
