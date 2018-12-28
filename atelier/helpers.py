from flask import request, url_for, redirect


def redirect_url(default="home"):
    return request.args.get('next') or request.referrer or url_for(default)


def redirect_prev():
    return redirect(redirect_url())
