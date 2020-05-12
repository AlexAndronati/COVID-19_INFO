from flask import current_app as app
from data_worker import DataWorker
from flask import Flask, render_template, request
import logging


@app.route("/", methods=["GET", "POST"])
def foo2(data=None):
    country_table = DataWorker.get_country_table()
    DataWorker.get_global_plot()
    app.logger.info(f'app logger {request}')

    return render_template("table.html", data=data, country_table=country_table)


@app.route("/country", methods=["GET", "POST"])
def country(ctr=None):
    app.logger.info(request)

    if request.method == "POST":
        ctr = request.form["country"]  # ctr - chosen country
        df = DataWorker.get_table(ctr)
        DataWorker.create_plot(ctr)
        app.logger.info(f'Requesting data for {ctr}')
        if df is None:
            app.logger.info(f"Can't get {ctr} dataframe")

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
