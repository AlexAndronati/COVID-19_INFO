import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from os import path
from settings import DB_URL, DB_NAME
from sqlalchemy import create_engine
from scipy import optimize


class DataWorker:
    engine = create_engine(DB_URL)
    df = pd.read_sql_query(f'select * from "{DB_NAME}"', con=engine)
    df_general_info = None

    @classmethod
    def DB_update(cls):
        df_update = pd.read_json("https://api.covid19api.com/all")
        d = cls.df['Date'].max()
        d = d.strftime('%Y-%m-%d')
        df_update = df_update[df_update["Date"] > d]
        df_update = cls.df_process(df_update)

        df_update.to_sql(DB_NAME, con=cls.engine, if_exists='append')
        cls.df = cls.df.append(df_update, ignore_index=True)

        for f in os.listdir("static/"):
            if f != "favicon.ico":
                os.remove(f"static/{f}")

    @staticmethod
    def df_process(df: pd.DataFrame):
        df.drop(columns=["Lat", "Lon", "CountryCode", "CityCode"], inplace=True)
        df.rename(columns={"Province": "Province_State", 'Confirmed': 'ConfirmedCases', 'Deaths': 'Fatalities',
                           'Country': 'Country_Region'}, inplace=True)
        df.index.name = 'Id'
        df = df.replace(r'^\s*$', np.nan, regex=True)

        df['Date'] = df['Date'].dt.date

        df_no_province = df.copy().dropna(subset=['Province_State'])
        df_no_province = df_no_province.sort_values(by=["Country_Region", "Date"])

        date_group = df_no_province.groupby(by="Date")
        df_no_p = pd.DataFrame(columns=[
            "Country_Region",
            "Province_State",
            "City",
            "ConfirmedCases",
            "Fatalities",
            "Recovered",
            "Active",
            "Date"])

        for date, group in date_group:
            ctr_group = group.groupby(by="Country_Region")
            for ctr, gr in ctr_group:

                temp = pd.DataFrame(
                    [[
                        gr.iloc[0].Country_Region,
                        gr.iloc[0].Province_State,
                        gr.iloc[0].City,
                        gr["ConfirmedCases"].sum(),
                        gr["Fatalities"].sum(),
                        gr["Recovered"].sum(),
                        gr["Active"].sum(),
                        date,
                    ]], columns=[
                        "Country_Region",
                        "Province_State",
                        "City",
                        "ConfirmedCases",
                        "Fatalities",
                        "Recovered",
                        "Active",
                        "Date"])
                df_no_p = df_no_p.append(temp)

        df_no_p.drop(['Province_State', "City"], axis=1, inplace=True)
        countries_with_regions = list(df_no_p.Country_Region.unique())
        indexNames = df[df['Country_Region'].isin(countries_with_regions)].index
        df = df.drop(indexNames)
        df.drop(columns=["Province_State", "City"], inplace=True)

        df_final = pd.concat([df, df_no_p], ignore_index=True)
        df_final.sort_values(by=["Country_Region", "Date"], inplace=True)
        df = df_final
        return df

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
    # def get_forecast(cls, dtf):
    #     x = np.arange(len(dtf["new"]))
    #     y = dtf["new"].values

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

            param = "Active"
            length = len(df_country[param])

            x = np.arange(length)
            y = df_country[param].values
            plt.plot(x, y, label="data")
            try:
                gaussian_model, cov = optimize.curve_fit(gaussian_f,
                                                         x,
                                                         y,
                                                         p0=[1, np.mean(df_country[param]), np.mean(df_country[param])],
                                                         maxfev=2000)

            # plt.plot(list(range(length)),
            #          gaussian_f(list(range(length)), gaussian_model[0], gaussian_model[1], gaussian_model[2]),
            #          color="green")

                plt.plot(list(range(length, length + 30)),
                         gaussian_f(list(range(length, length + 30)),
                         gaussian_model[0],
                         gaussian_model[1],
                         gaussian_model[2]),
                         color="red",
                         label="prognosis (30 days)")
            except:
                pass
            # ax = df_country.plot(
            #                     x="Date",
            #                     y=["ConfirmedCases", "Fatalities", "Recovered", "Active"],
            #                     grid=True,
            #                     rot=90
            #
            # )
            plt.savefig(f"static/{country}.png", format='png')
            plt.clf()



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
                                grid=True,
                                rot=90

            )
            plt.savefig("static/df_global.png", format='png')
            plt.clf()


def gaussian_f(x:list, a, b, c):
    y = a * np.exp(-0.5 * ((x-b)/c)**2)
    return y


if __name__ == '__main__':
    DataWorker.DB_update()

