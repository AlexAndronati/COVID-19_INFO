
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from settings import DB_URL, API_URL_ALL, DB_NAME
from data_worker import DataWorker

import psycopg2


df = pd.read_json(API_URL_ALL)
df = DataWorker.df_process(df)
#
# df.drop(columns=["Lat", "Lon", "CountryCode", "CityCode"], inplace=True)
# df.rename(columns={"Province": "Province_State", 'Confirmed': 'ConfirmedCases', 'Deaths': 'Fatalities',
#                    'Country': 'Country_Region'}, inplace=True)
# df.index.name = 'Id'
# df = df.replace(r'^\s*$', np.nan, regex=True)
#
# df['Date'] = df['Date'].dt.date
# # try:
# #     df['Date'] = df['Date'].dt.date
# # except Exception:
# #     pass
#
# # group_country = df.groupby(by="Country_Region")
# # print(df)
# df_no_province = df.copy().dropna(subset=['Province_State'])
# df_no_province = df_no_province.sort_values(by=["Country_Region", "Date"])
#
# date_group = df_no_province.groupby(by="Date")
# df_no_p = pd.DataFrame(columns=[
#     "Country_Region",
#     "Province_State",
#     "City",
#     "ConfirmedCases",
#     "Fatalities",
#     "Recovered",
#     "Active",
#     "Date"])
#
# for date, group in date_group:
#     ctr_group = group.groupby(by="Country_Region")
#     for ctr, gr in ctr_group:
#         #         print(gr.head(50))
#         #         print(gr["ConfirmedCases"].sum())
#         temp = pd.DataFrame(
#             [[
#                 gr.iloc[0].Country_Region,
#                 gr.iloc[0].Province_State,
#                 gr.iloc[0].City,
#                 gr["ConfirmedCases"].sum(),
#                 gr["Fatalities"].sum(),
#                 gr["Recovered"].sum(),
#                 gr["Active"].sum(),
#                 date,
#             ]], columns=[
#                 "Country_Region",
#                 "Province_State",
#                 "City",
#                 "ConfirmedCases",
#                 "Fatalities",
#                 "Recovered",
#                 "Active",
#                 "Date"])
#         df_no_p = df_no_p.append(temp)
#
# df_no_p.drop(['Province_State', "City"], axis=1, inplace=True)
# countries_with_regions = list(df_no_p.Country_Region.unique())
# indexNames = df[df['Country_Region'].isin(countries_with_regions)].index
# df = df.drop(indexNames)
# df.drop(columns=["Province_State", "City"], inplace=True)
#
# df_final = pd.concat([df, df_no_p], ignore_index=True)
# df_final.sort_values(by=["Country_Region", "Date"], inplace=True)
# df = df_final


engine = create_engine(DB_URL)
df.to_sql(DB_NAME, engine, if_exists='replace')





