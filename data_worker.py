import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from flask import Flask
from sqlalchemy import create_engine
from os import path
from settings import DB_URL, DB_NAME


class DataWorker:
    engine = create_engine(DB_URL)
    df = pd.read_sql_query(f'select * from "{DB_NAME}"', con=engine)
    df_general_info = None

    @classmethod
    def DB_update(cls):
        pass

    @classmethod
    def get_country_table(cls):
        if cls.df_general_info is None:

            cls.df_general_info = pd.DataFrame(columns=["Country_Region",
                                                    "ConfirmedCases",
                                                    "Fatalities",
                                                    "Recovered",
                                                    "Active"])
            group_country = cls.df.groupby(by="Country_Region")

            for country, group in group_country:
                temp = pd.DataFrame([[
                                      country,
                                      group.tail(1).iloc[0]['ConfirmedCases'],
                                      group.tail(1).iloc[0]['Fatalities'],
                                      group.tail(1).iloc[0]['Recovered'],
                                      group.tail(1).iloc[0]['Active'],
                                    ]], columns=[
                                      "Country_Region",
                                      "ConfirmedCases",
                                      "Fatalities",
                                      "Recovered",
                                      "Active"])
                cls.df_general_info = cls.df_general_info.append(temp)

        return cls.df_general_info

    @classmethod
    def get_table(cls, country):
        df = cls.df
        df = df.copy()[df["Country_Region"] == country]
        df.dropna(axis=1, inplace=True)
        df.drop(['Country_Region', "index"], axis=1, inplace=True)
        return df

    # @classmethod
    # def upload_data_to_sql(cls, df=None):
    #     engine = create_engine('postgresql+psycopg2://postgres:admin@127.0.0.1:5433/check')
    #     if df is None:
    #         df = cls.df
    #     df.to_sql('check', engine, if_exists='replace')

    @classmethod
    def create_plot(cls, country):
        if not path.exists(f"static/{country}"):
            df_country = cls.get_table(country)
            df_country.plot(
                                x="Date",
                                y=["ConfirmedCases", "Fatalities", "Recovered", "Active"],
                                grid=True
                                )
            plt.savefig(f"static/{country}.png", format='png')

    @classmethod
    def get_global_plot(cls):

        if not path.exists("static/df_global.png"):
            df = cls.df
            date_group = df.groupby(by="Date")
            df_global = pd.DataFrame(columns=[
                                      "Date",
                                      "ConfirmedCases",
                                      "Fatalities",
                                      "Recovered",
                                      "Active"])
            for date, group in date_group:
                temp = pd.DataFrame(
                    [[
                        date,
                        group["ConfirmedCases"].sum(),
                        group["Fatalities"].sum(),
                        group["Recovered"].sum(),
                        group["Active"].sum(),
                    ]],
                    columns=[
                        "Date",
                        "ConfirmedCases",
                        "Fatalities",
                        "Recovered",
                        "Active"]
                )
                df_global = df_global.append(temp)
            df_global.plot(
                                x="Date",
                                y=["ConfirmedCases", "Fatalities", "Recovered", "Active"],
                                grid=True
                                )
            plt.savefig("static/df_global.png", format='png')


if __name__ == '__main__':
    print(DataWorker.get_country_table())

