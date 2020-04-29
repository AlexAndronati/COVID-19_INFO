import random
import string
import json
from data_worker import get_country_list, get_table

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def foo2(data=None):
    country_list = get_country_list()

    return render_template("table.html", data=data, country_list=country_list)


@app.route("/country", methods=["GET", "POST"])
def country(ctr=None):

    if request.method == "POST":
        ctr = request.form["country"]  # ctr - chosen country
        df = get_table(ctr)

        return render_template("country_data.html", df_country=df)

    return ":("


if __name__ == '__main__':
    app.run()

