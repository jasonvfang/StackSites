# -*- coding: utf-8 -*-
from flask.ext.assets import Bundle, Environment

css = Bundle(
    "libs/font-awesome4/css/font-awesome.css",
    "libs/bootstrap3/css/bootstrap.css",
    "css/public/home.css",
    filters="cssmin",
    output="public/css/common.css"
)

js = Bundle(
    "libs/jquery2/jquery-2.0.3.min.js",
    "libs/bootstrap3/js/bootstrap.min.js",
    "js/utils.js", filters='jsmin',
    output="public/js/common.js"
)

assets = Environment()

assets.register("js_all", js)
assets.register("css_all", css)