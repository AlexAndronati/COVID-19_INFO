import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import io
import matplotlib.pyplot as plt
from flask import send_file
from flask import Flask


class DataWorker:

    df = pd.read_json('https://api.covid19api.com/all')
    df.drop(columns=["Lat", "Lon", "CountryCode", "CityCode"], inplace=True)
    df.rename(columns={"Province": "Province_State", 'Confirmed': 'ConfirmedCases', 'Deaths': 'Fatalities',
                       'Country': 'Country_Region'}, inplace=True)
    df.index.name = 'Id'
    df = df.replace(r'^\s*$', np.nan, regex=True)

    df['Date'] = df['Date'].dt.date
    try:
        df['Date'] = df['Date'].dt.date
    except Exception:
        pass

    # group_country = df.groupby(by="Country_Region")
    # print(df)
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
            #         print(gr.head(50))
            #         print(gr["ConfirmedCases"].sum())
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
    df_final = pd.concat([df, df_no_p], ignore_index=True)
    df_final.sort_values(by=["Country_Region", "Date"], inplace=True)
    df = df_final

    @classmethod
    def get_country_list(cls):
        country_list = list(cls.df["Country_Region"].unique())
        return country_list

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
        # print(df_country)

        ax = df_country.plot(
                            x="Date",
                            y=["ConfirmedCases", "Fatalities", "Recovered", "Active"],
                            grid=True
                            )

        plt.savefig("static/fig1.png", format='png')
        # print(ax)
        # print(type(ax))
        # fig = ax.get_figure()
        # fig.write_image("static/fig1.png")
        # plt.show()

        # bytes_image = io.BytesIO()
        # plt.savefig(bytes_image, format='png')
        # bytes_image.seek(0)
        # return bytes_image


if __name__ == '__main__':
    # DataWorker.get_table("Albania")
    DataWorker.create_plot("Ukraine")
