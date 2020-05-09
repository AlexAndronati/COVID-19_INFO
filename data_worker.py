import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import io
import matplotlib.pyplot as plt
from flask import send_file
from flask import Flask
from sqlalchemy import create_engine


class DataWorker:
    engine = create_engine('postgresql+psycopg2://postgres:admin@127.0.0.1:5433/covid')
    df = pd.read_sql_query('select * from "covid"', con=engine)

    @classmethod
    def get_country_table(cls):

        df_general_info = pd.DataFrame(columns=["Country_Region",
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
            df_general_info = df_general_info.append(temp)

        # country_list = list(cls.df["Country_Region"].unique())
        return df_general_info

    @classmethod
    def get_table(cls, country):
        df = cls.df
        df = df.copy()[df["Country_Region"] == country]
        df.dropna(axis=1, inplace=True)
        df.drop(['Country_Region', ], axis=1, inplace=True)
        return df

    # @classmethod
    # def upload_data_to_sql(cls, df=None):
    #     engine = create_engine('postgresql+psycopg2://postgres:admin@127.0.0.1:5433/check')
    #     if df is None:
    #         df = cls.df
    #     df.to_sql('check', engine, if_exists='replace')

    @classmethod
    def create_plot(cls, country):
        df_country = cls.get_table(country)
        df_country.plot(
                            x="Date",
                            y=["ConfirmedCases", "Fatalities", "Recovered", "Active"],
                            grid=True
                            )
        plt.savefig("static/fig1.png", format='png')

    @classmethod
    def get_global_plot(cls):
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
    # DataWorker.get_table("Albania")
    print(DataWorker.get_country_table())

