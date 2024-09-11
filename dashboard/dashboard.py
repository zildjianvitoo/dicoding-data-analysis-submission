import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set_theme(style="dark")


def create_season_rents(df):
    season_rents_df = df.groupby("season")["count"].sum().reset_index()
    return season_rents_df


def create_daily_rents(df):
    daily_rents_df = df.resample(rule="D", on="dateday").agg({"count": "sum"})
    daily_rents_df = daily_rents_df.reset_index()
    daily_rents_df = daily_rents_df.rename(columns={"count": "rent_in_a_day"})

    return daily_rents_df


def create_workingday_rents(df):
    return df.groupby("workingday")["count"].sum().reset_index()


def create_clustering(df):
    def categorize_temp(temp):
        if temp < 0.2:
            return "Dingin"
        elif temp < 0.6:
            return "Sedang"
        else:
            return "Panas"

    def categorize_windspeed(windspeed):
        if windspeed < 0.2:
            return "Pelan"
        elif windspeed < 0.6:
            return "Sedang"
        else:
            return "Kencang"

    df["temp_category"] = df["temperature"].apply(categorize_temp)
    df["windspeed_category"] = df["windspeed"].apply(categorize_windspeed)

    return df


day_hour_df = pd.read_csv("day_hour_data.csv")

day_hour_df["dateday"] = pd.to_datetime(day_hour_df["dateday"])

day_hour_df.sort_values(by="dateday", inplace=True)
day_hour_df.reset_index(inplace=True)


min_date = day_hour_df["dateday"].min()
max_date = day_hour_df["dateday"].max()


with st.sidebar:
    st.image(
        "https://media.istockphoto.com/id/1269161415/id/vektor/sepeda-bersepeda-ikon-naik-vektor-sederhana-pada-latar-belakang-putih-terisolasi.jpg?s=612x612&w=0&k=20&c=p4v8JYqg58jEDljR8MT5fz9BkEkoo8rrFqQ9JiE3sbU="
    )

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

main_df = day_hour_df[
    (day_hour_df["dateday"] >= str(start_date))
    & (day_hour_df["dateday"] <= str(end_date))
]

daily_rents_df = create_daily_rents(main_df)
season_rents_df = create_season_rents(main_df)
workingday_rents_df = create_workingday_rents(main_df)
clustering_rents_df = create_clustering(main_df)

st.header("Bicycle Rents")
st.subheader("Daily rents")
(col1,) = st.columns(1)

with col1:
    total_rents = daily_rents_df.rent_in_a_day.sum()
    st.metric("Total bicycle rents", value=format(total_rents, ",").replace(",", "."))

fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
    daily_rents_df["dateday"],
    daily_rents_df["rent_in_a_day"],
    marker="o",
    linewidth=2,
    color="#90CAF9",
)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)

st.pyplot(fig)

## Section 2
st.subheader("Best & Worst Season to Rents")
fig, ax = plt.subplots(figsize=(35, 15))


max_rents_season = season_rents_df["count"].idxmax()
colors = [
    "#D3D3D3" if i != max_rents_season else "#90CAF9" for i in season_rents_df.index
]

season_rents_df["season"] = season_rents_df["season"].map(
    {1: "spring", 2: "summer", 3: "fall", 4: "winter"}
)

sns.barplot(
    x="season",
    y="count",
    data=season_rents_df,
    palette=colors,
)
ax.set_ylabel(None)
ax.set_xlabel("Name of Season", fontsize=30)
ax.set_title("Best Performing Season", loc="center", fontsize=50)
ax.tick_params(axis="y", labelsize=35)
ax.tick_params(axis="x", labelsize=30)
st.pyplot(fig)

## Section 3
st.subheader("Working Day vs Not Working Day")
fig, ax = plt.subplots()
labels = ["Not Working Day", "Working Day"]
ax.pie(
    data=workingday_rents_df,
    autopct="%1.2f%%",
    labels=labels,
    x="count",
    colors=["#D3D3D3", "#90CAF9"],
)
st.pyplot(fig)

## Section 4
st.subheader("Clustering rents based on windspeed and temperature")
fig, ax = plt.subplots(figsize=(12, 8))
sns.scatterplot(
    data=clustering_rents_df,
    x="temperature",
    y="count",
    hue="temp_category",
    style="windspeed_category",
    palette="coolwarm",
)
ax.set_xlabel("Temperature")
ax.set_xlabel("Count of Bicycle rents")
ax.set_title("Temp and windspeed category")
st.pyplot(fig)
