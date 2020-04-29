import pandas as pd


def get_country_list():
    df = pd.read_csv("D:/Документы/Универ/Python/datasets/train.csv")
    df.set_index("Id")
    country_list = list(df["Country_Region"].unique())

    return country_list


def get_table(country):
    df = pd.read_csv("D:/Документы/Универ/Python/datasets/train.csv")
    df.set_index("Id")
    df = df[df["Country_Region"] == country]

    return df


if __name__ == '__main__':
    get_table("Albania")
