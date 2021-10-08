import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly
import plotly.io as pio
import plotly.express as px
import plotly.graph_objs as go
import plotly.offline as pyo

import streamlit as st

df = pd.read_csv("C:/Users/Roshan Maur/Downloads/archive/results.csv")
df["date"] = pd.to_datetime(df["date"])

st.header("International Football Statistics")
st.write("""
#### You can check your favourite international team's W/L/D record.
""")

@st.cache
def wins_or_losses_or_draws(country_name):
    
    home = df[df["home_team"]==country_name]
    away = df[df["away_team"]==country_name]
    
    home_wins = home[home["home_score"]>home["away_score"]]
    away_wins = away[away["away_score"]>away["home_score"]]
    
    home_def = home[home["home_score"]<home["away_score"]]
    away_def = away[away["away_score"]<away["home_score"]]
    
    home_d = home[home["home_score"]==home["away_score"]]
    away_d = away[away["away_score"]==away["home_score"]]
    
    wins = len(home_wins) + len(away_wins)
    defeats = len(home_def) + len(away_def)
    draws = len(home_d) + len(away_d)
    
    return [wins, defeats, draws]

home = df["home_team"].unique().tolist()
away = df["away_team"].unique().tolist()

l = []
m = []

for x in home:
    if x not in away:
        l.append(x)
        
for y in away:
    if y not in home:
        m.append(y)

big_list = []

for x in home:
    if x in away:
        big_list.append(x)

big_list.extend(m)
big_list.extend(l)

stats_df = pd.DataFrame(big_list)

stats_df.columns = ["teams"]

stats_df["total"] = stats_df["teams"].apply(lambda x: wins_or_losses_or_draws(x))

stats_df["win"] = stats_df["total"].apply(lambda x: x[0])
stats_df["defeats"] = stats_df["total"].apply(lambda x: x[1])
stats_df["draws"] = stats_df["total"].apply(lambda x: x[2])

stats_df.drop("total", axis=1, inplace=True)
stats_df["matches_played"] = stats_df["win"] + stats_df["defeats"] + stats_df["draws"]

st.sidebar.header("Sidebar")
teams = sorted(stats_df["teams"])
selected_team = st.sidebar.selectbox("Teams",teams)

st.sidebar.markdown("""
<br>
""", True)

selected_data = stats_df[stats_df["teams"]==selected_team][["win", "defeats", "draws"]]
arr = np.array(selected_data)
final_team = arr.flatten().tolist()
matches = sum(final_team)

fig = px.pie(values=final_team, title=selected_team, names=["wins", "defeats", "draws"], template="presentation", hole=0,
color_discrete_sequence=['green', "yellow", "red"])
fig.update_traces(textinfo="percent+value", pull=[0,0.2,0], rotation=290)

st.plotly_chart(fig)
st.write("{} has {} wins, {} draws and {} defeats in {} matches".format(selected_team, final_team[0], final_team[1], final_team[2], matches))

euro = df[df["tournament"]=="UEFA Euro"]
euro["year"] = euro["date"].dt.year
euro_year = st.sidebar.selectbox("Euro Year", euro["year"].unique())

@st.cache
def euro_winner(year):
    
    that_year = euro[euro["year"]==year]
    final = that_year.iloc[-1]
    home_score = final["home_score"]
    away_score = final["away_score"]
    
    statement = str(final["home_team"]) + " " + str(home_score) + " - " + str(away_score) + " " + str(final["away_team"])
    
    return statement

euro_score = euro_winner(euro_year)
st.sidebar.write("UEFA Euro {} Final Score".format(euro_year))
st.sidebar.write(euro_score)

st.sidebar.markdown("""
<hr>
""", True)

copa = df[df["tournament"]=="Copa América"]
copa["year"] = copa["date"].dt.year
copa_year = st.sidebar.selectbox("Copa América Year", copa["year"].unique())

@st.cache
def copa_winner(year):
    
    that_year = copa[copa["year"]==year]
    final = that_year.iloc[-1]
    home_score = final["home_score"]
    away_score = final["away_score"]
    
    statement = str(final["home_team"]) + " " + str(home_score) + " - " + str(away_score) + " " + str(final["away_team"])
    
    return statement

copa_score = copa_winner(copa_year)
st.sidebar.write("Copa América {} Final Score".format(copa_year))
st.sidebar.write(copa_score)

st.sidebar.markdown("""
<hr>
""", True)

wc = df[df["tournament"]=="FIFA World Cup"]
wc["year"] = wc["date"].dt.year
wc_year = st.sidebar.selectbox("FIFA World Cup Year", wc["year"].unique())

@st.cache
def wc_winner(year):
    
    that_year = wc[wc["year"]==year]
    final = that_year.iloc[-1]
    home_score = final["home_score"]
    away_score = final["away_score"]
    
    statement = str(final["home_team"]) + " " + str(home_score) + " - " + str(away_score) + " " + str(final["away_team"])
    
    return statement

wc_score = wc_winner(wc_year)
st.sidebar.write("FIFA World Cup {} Final Score".format(wc_year))
st.sidebar.write(wc_score)