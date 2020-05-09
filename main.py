import random
import string
import json
# import logging

from data_worker import DataWorker

from flask import Flask, render_template, request, url_for
from flask import send_file

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# logging.basicConfig(filename='logs/countries.log', level=logging.DEBUG)


@app.route("/", methods=["GET", "POST"])
def foo2(data=None):
    country_table = DataWorker.get_country_table()
    DataWorker.get_global_plot()
    # if country_list is not None:
    #     app.logger.info('Country list uploaded succesfully')
    # else:
    #     app.logger.info('Failed uploading Country list')

    return render_template("table.html", data=data, country_table=country_table)


@app.route("/country", methods=["GET", "POST"])
def country(ctr=None):

    if request.method == "POST":
        ctr = request.form["country"]  # ctr - chosen country

        df = DataWorker.get_table(ctr)

        bytes_obj = DataWorker.create_plot(ctr)

        return render_template("country_data.html", df_country=df, country=ctr)

    return ":("


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-store"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.errorhandler(404)
def page_not_found(error):
    return "ooops", error


if __name__ == '__main__':
    app.run()

