# importing all the required libraries
import pandas as pd
import numpy as np

import plotly
import plotly.express as px
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc

from datetime import date
from helper import *
from datetime import datetime as dt

# reading the datasets from github using pandas
recovered_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
deaths_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
confirmed_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
country_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv")

# using a custom function to convert the column names into lowercase
recovered_df = make_it_smaller(recovered_df)
country_df = make_it_smaller(country_df)
deaths_df = make_it_smaller(deaths_df)
confirmed_df = make_it_smaller(confirmed_df)

# renaming columns
recovered_df = recovered_df.rename(columns={"province/state":"state", "country/region":"country"})
deaths_df = deaths_df.rename(columns={"province/state":"state", "country/region":"country"})
confirmed_df = confirmed_df.rename(columns={"province/state":"state", "country/region":"country"})
country_df = country_df.rename(columns = {"country_region":"country"})

# using the pd.melt function to reshape the dataset to convert it into a long dataset instead of wide dataset
new_recovered_df = pd.melt(recovered_df, id_vars=["state", "country", "lat", "long"], var_name="date", value_name="recovered")
new_confirmed_df = pd.melt(confirmed_df, id_vars=["state", "country", "lat", "long"], var_name="date", value_name="confirmed")
new_deaths_df = pd.melt(deaths_df, id_vars=["state", "country", "lat", "long"], var_name="date", value_name="deaths")

# dropping the state column
new_recovered_df.drop(["state"], axis=1, inplace=True)
new_confirmed_df.drop(["state"], axis=1, inplace=True)
new_deaths_df.drop(["state"], axis=1, inplace=True)

# converting the date column into pandas datetime object
new_confirmed_df["date"] = pd.to_datetime(new_confirmed_df["date"])
new_deaths_df["date"] = pd.to_datetime(new_deaths_df["date"])
new_recovered_df["date"] = pd.to_datetime(new_recovered_df["date"])

# sorting values
new_confirmed_df =  new_confirmed_df.sort_values(by="date")
new_deaths_df = new_deaths_df.sort_values(by="date")
new_recovered_df = new_recovered_df.sort_values(by="date")

# Taking care of the United Kingdom bug
new_recovered_df.loc[new_recovered_df["country"]=="United Kingdom", ["country"]] = new_recovered_df[
    new_recovered_df["country"]=="United Kingdom"].apply(
    lambda x: x.astype(str).str.replace("United Kingdom", "UK"))

new_deaths_df.loc[new_deaths_df["country"]=="United Kingdom", ["country"]] = new_deaths_df[
    new_deaths_df["country"]=="United Kingdom"].apply(
    lambda x: x.astype(str).str.replace("United Kingdom", "UK"))

new_confirmed_df.loc[new_confirmed_df["country"]=="United Kingdom", ["country"]] = new_confirmed_df[
    new_confirmed_df["country"]=="United Kingdom"].apply(
    lambda x: x.astype(str).str.replace("United Kingdom", "UK"))

# top 10 countries with the most recoveries
best_recoveries = new_recovered_df.groupby(["country"])["recovered"].max().reset_index()
top_10_rec = best_recoveries.nlargest(10, columns="recovered")

# top 10 countries with the most deaths
most_deaths = new_deaths_df.groupby(["country"])["deaths"].max().reset_index()
top_deaths = most_deaths.nlargest(10, columns="deaths")

# top 10 countries with the most confirmed cases
most_con_cases = new_confirmed_df.groupby(["country"])["confirmed"].max().reset_index()
top_ten_con = most_con_cases.nlargest(10, columns="confirmed")

# merging the above data into a single dataframe
df_1 = pd.merge(most_con_cases, most_deaths, on="country")
df_true = pd.merge(df_1, best_recoveries, on="country")

# adding mortality rate, recovery rate and active cases
df_true["mortality_rate"] = (df_true["deaths"]/df_true["confirmed"])*100
df_true["recovery_rate"] = (df_true["recovered"]/df_true["confirmed"])*100
df_true["pending"] = (df_true["confirmed"])-(df_true["recovered"]+df_true["deaths"])

# top 10 countries with the best recovery rate
top_ten_r_rate = df_true.groupby(["country"])["recovery_rate"].max().reset_index().nlargest(11, columns="recovery_rate")
# top 10 countries with the highest mortality rate
top_ten_m_rate = df_true.groupby(["country"])["mortality_rate"].max().reset_index().nlargest(10, columns="mortality_rate")

# using a custom function to convert numbers into M,K or B
total_confirmed = convert_to_mil_thousand(df_true["confirmed"].sum())
total_recoverd = convert_to_mil_thousand(df_true["recovered"].sum())
total_deaths = convert_to_mil_thousand(df_true["deaths"].sum())

# using custom functions to get the country names, country codes and continent names
df_true["country_code"] = df_true["country"].apply(lambda x: get_country_code(x))
df_true["continent_code"] = df_true["country_code"].apply(lambda x: get_continent_code(x))
df_true["continent"] = df_true["continent_code"].apply(lambda x: get_continent_name(x))

df_true.drop([48,105], axis="index", inplace=True)

df_true.loc[27, "continent"] = "Asia"
df_true.loc[39, "continent"] = "Africa"
df_true.loc[40, "continent"] = "Africa"
df_true.loc[42, "continent"] = "Africa"
df_true.loc[75, "continent"] = "Europe"
df_true.loc[92, "continent"] = "Asia"
df_true.loc[93, "continent"] = "Europe"
df_true.loc[170, "continent"] = "Asia"
df_true.loc[174, "continent"] = "Asia"
df_true.loc[179, "continent"] = "Europe"
df_true.loc[180, "continent"] = "North America"
df_true.loc[189, "continent"] = "Asia"

df_true["world"] = "world"

# This chunk of code was specifically written for animated choropleth
df1 = pd.merge(new_confirmed_df, new_deaths_df, on=["date", "lat", "long", "country"])
df = pd.merge(new_recovered_df, df1, on=["date", "lat", "long", "country"])
df["country_code"] = df["country"].apply(lambda x: get_country_code(x))
df["continent_code"] = df["country_code"].apply(lambda x: get_continent_code(x))
df["continent"] = df["continent_code"].apply(lambda x: get_continent_name(x))
df["date_str_all"] = df["date"].apply(lambda x: str(x))
con = df.drop(["recovered", "deaths"], axis=1)
con_date = con.groupby([pd.Grouper(key="date", freq="1D"), "country"])["confirmed"].max()
confirmed = con_date.to_frame().reset_index()
confirmed['date_str'] = confirmed['date'].apply(lambda x: str(x))
confirmed["new_date_str"] = confirmed["date_str"].apply(lambda x: x.split(" ")[0])

max_date = confirmed["date"].max()
max_date_choro = dt(max_date.year, max_date.month, max_date.day)

# ------------------- DASH BEGINS HERE -------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], eager_loading=True)
app.title = "Covid-19 Dashboard"

country_names = []
for i in df_true.country.unique():
    country_names.append({"label":str(i), "value":str(i)})

column_names = [{"label":"Confirmed Cases", "value":"confirmed"},
               {"label":"Deaths", "value":"deaths"},
               {"label":"Recovered Cases", "value":"recovered"}]

# -------------------- DASH LAYOUT ------------------------------------
app.layout = html.Div([
    dbc.Container([dbc.Row([
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Confirmed Cases", style={"font_family":["Montserrat", "sans-serif"], "color":"red"}),
                        html.B(
                            html.H3(total_confirmed, style={"color":"red"}),
                        ),
                    ])
                ]),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Recovered Cases", style={"font_family":["Montserrat", "sans-serif"], "color":"#7CFC00"}),
                        html.B(
                            html.H3(total_recoverd, style={"color":"#7CFC00"}),
                        ),
                    ])
                ]), 
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Deaths", style={"font_family":["Montserrat", "sans-serif"], "color":"#D3D3D3"}),
                        html.B(
                            html.H3(total_deaths, style={"color":"#D3D3D3"}),
                        ),
                    ]),
                ]),
            ]),
        ]),
    ]),
    html.Br(),
    html.Div([
        html.H5(["Select a country"], style={"textAlign":"center"}),
        dcc.Dropdown(id="country_picker", options=country_names, value="India", searchable=True, 
                style={"align-items": "center", "justify-content": "center", "color":"black"}),
        ], style={"width":"50%", "marginLeft":"25%"}),
]),
    
    dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                html.H4("Confirmed Cases", className="card-text", style={"font_family":["Montserrat", "sans-serif"], "color":"red"}),
                html.H4(id="confirmed", style={"color":"red"}),
                ]),
            ], className="mb-4", outline=True),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Recovered Cases", className="card-text", style={"font_family":["Montserrat", "sans-serif"], "color":"#7CFC00"}),
                    html.H4(id="recovered", style={"color":"#7CFC00"}),
                ])
            ], className="mb-4"),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Deaths", className="card-text", style={"font_family":["Montserrat", "sans-serif"], "color":"#D3D3D3"}),
                    html.H4(id="deaths", style={"color":"#D3D3D3"}),
                ]),
            ], className="mb-4"),
        ], width={"size":3}),

        dbc.Col([
            dbc.Card([
                dcc.Graph(id="pie_individual"),
            ], inverse=True, style={"width":"100%"}),
        ], width={"size":4, "offset":-8}),

        dbc.Col([
            dbc.Card([
                dcc.Graph(id="line_chart")
            ])
        ], width=5)
    ]),
    ], fluid=True),

    html.Br(),
    html.Br(),
    dbc.Container([
        html.Div([
            html.H5("Visualizing the top 25 countries differently",  style={"textAlign":"center"}),
            dcc.Dropdown(id="sunburst_columns", options=column_names, value="confirmed", 
            style={"align-items": "center", "justify-content": "center", "color":"black"}),
        ], style={"width":"50%", "marginLeft":"25%"}),
        html.Br(),
    ]),
    
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.P("This is a Sunburst chart. This is like a hierarchical pie-chart. It is currently displaying the 25 countries with the most confirmed cases segregated based on their respective continents.", className="card-text",
                    style={"textAlign":"center"}),
                    dcc.Graph(id="sunburst")
                ]),
            ], width=5),
            dbc.Col([
                dbc.Card([
                    html.P("This is a TreeMap. This is like a hierarchical display of data in a nested rectangular form. This currently displays the 25 countries with the most confirmed cases segregated based on their respective continents.",
                        className="card-text", style={"textAlign":"center"}),
                    dcc.Graph(id="treemap")
                ]),
            ], width=7)
        ])
    ], fluid=True),

    html.Br(),
    html.Br(),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H5("Select a start date and an end date", style={"text-align":"center"}),
                html.Div([
                    dcc.DatePickerRange(id='my-date-picker-range', min_date_allowed=dt(2020,1,22), 
                                    day_size=45, minimum_nights=10, reopen_calendar_on_clear=True, clearable=True, persistence=True,
                                    max_date_allowed= max_date_choro, persisted_props=["start_date"],
                                    initial_visible_month=date(2020, 1, 1), display_format='MMM Do, YYYY',
                                    first_day_of_week=0, persistence_type="session",
                                    start_date=dt(2020,1,22).date(), end_date=max_date_choro.date(), updatemode="bothdates",
                                    style={"align-items": "center", "justify-content": "center", "color":"black",
                                        "width":"120%", "height":"35px"}),
                    html.Br(),
                    html.Br(),
                ], style={"width":"50%", "align-items":"center", "margin-left":"30%"}),
                dbc.Card([
                    html.P("This is an animated choropleth map to display the rise of confirmed cases. Please note that there should be a minimum difference of 10 days between the start date and end date.",
                        style={"textAlign":"center"}, className="card-text"),
                    dcc.Graph(id="animated_choro"),
                ]),
        ], width=7),

            dbc.Col([
                html.Div([
                    html.H5("Visualize the earth", style={"text-align":"center"}),
                    dcc.Dropdown(id="ortho_id", options=column_names, value="confirmed",
                            style={"align-items": "center", "justify-content": "center", "color":"black"}),
                    html.Br(),
                ], style={"width":"50%", "align-items":"center", "margin":"auto"}),
                dbc.Card([
                    html.P("This is an orthographic chart aka projection of natural earth. You can select the type of data you want to analyze from the above dropdown.",
                    className="card-text", style={"textAlign":"center"}),
                    dcc.Graph(id="ortho_earth")
                ]),
            ], width=5)
        ])
    ], fluid=True),

    html.Br()
]) 

# ------------------- DASH REGULAR CALLBACKS -------------------------------
@app.callback(Output("pie_individual", "figure"),
             [Input("country_picker", "value")])
def make_a_eco_friendly_pie_chart(country_picker):
    hover_pie = "%{label} <br>%{value} </br>"
    df = df_true.loc[df_true["country"]==country_picker]
    vals = df[["pending", "recovered", "deaths"]].values.flatten().tolist()
    fig = px.pie(values=vals, names=["Active cases", "Recovered cases", "Deaths"],
                 title="Covid-19 for {}".format(country_picker),
                color_discrete_sequence=["red", "#7CFC00", "grey"], template="plotly_dark")
    
    fig.update_traces(textinfo="label+percent", rotation=180, pull=[0.3,0,0], hoverinfo="label+percent",
                     marker=dict(line=dict(color="white", width=3)),
                     hovertemplate=hover_pie)

    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0),
                        font=dict(family="Times New Roman, monospace", size=15),
                        title_font_size=25, title={'y':0.94, 'x':0.35, 'xanchor': 'center','yanchor': 'top'},
                        hoverlabel=dict(font_size=16, font_family="Rockwell"))
    
    return fig

@app.callback([Output("confirmed", "children"),
            Output("recovered", "children"), Output("deaths", "children")],
            [Input("country_picker", "value")])
def country_confirmed(country_picker):

    df = df_true.loc[df_true["country"]==country_picker]
    vals = df[["pending", "recovered", "deaths"]].values.flatten().tolist()

    return (convert_to_mil_thousand(sum(vals)), convert_to_mil_thousand(vals[1]), convert_to_mil_thousand(vals[2]))

@app.callback(Output("line_chart", "figure"),
            [Input("country_picker", "value")])
def country_line_chart(country_picker):

    country_con = new_confirmed_df[new_confirmed_df["country"]==country_picker]
    country_rec = new_recovered_df[new_recovered_df["country"]==country_picker]
    country_deaths = new_deaths_df[new_deaths_df["country"]==country_picker]

    dfso = pd.merge(country_con, country_rec, on=["date", "lat", "long", "country"])
    df_org = pd.merge(dfso, country_deaths, on=["date", "lat", "long", "country"])

    confirmed = go.Scatter(x=df_org["date"], y=df_org["confirmed"], name="Confirmed",
                    line=dict(color='firebrick'), mode="lines")
    recovered = go.Scatter(x=df_org["date"], y=df_org["recovered"], name="Recovered",
                        line=dict(color='green'), mode="lines")
    deaths = go.Scatter(x=df_org["date"], y=df_org["deaths"], name="Deaths",
                        line=dict(color='#D3D3D3'), mode="lines")
                        
    real_data = [confirmed, recovered, deaths]
    title = "Covid-19 Analysis of {}".format(country_picker)

    layout = go.Layout(title=title, template="plotly_dark")

    fig = go.Figure(data=real_data, layout=layout)

    fig.update_layout(font=dict(family="Lato, monospace", size=15),
                    title_font_size=22, title={'y':0.94, 'x':0.35, 'xanchor': 'center','yanchor': 'top'},
                    hovermode="x unified")

    return fig

@app.callback(Output("sunburst", "figure"),
            [Input("sunburst_columns", "value")])
def sunburst_chart(sunburst_columns):

    df_true[182, "continent"] = "North America"
    df_true[180, "continent"] = "Europe"
    sub_df = df_true.groupby(["country", "continent"])[sunburst_columns].max().nlargest(25).reset_index()

    hover_sunburst_con = "Country: %{label} <br>Confirmed Cases: %{value}</br>"
    hover_sunburst_rec = "Country: %{label} <br>Confirmed Cases: %{value}</br>"
    hover_sunburst_d = "Country: %{label} <br>Confirmed Cases: %{value}</br>"

    if sunburst_columns=="confirmed":
        fig = px.sunburst(sub_df, values=sunburst_columns, path=["continent", "country"], template="plotly_dark",
                          color=sunburst_columns, color_continuous_scale=plotly.colors.sequential.Bluered)
        fig.update_layout(margin = dict(t=15, l=10, r=10, b=10), hoverlabel=dict(font_size=16, font_family="Rockwell"))
        fig.update_traces(hovertemplate=hover_sunburst_con)
    elif sunburst_columns=="deaths":
        fig = px.sunburst(sub_df, values=sunburst_columns, path=["continent", "country"], template="plotly_dark",
                          color=sunburst_columns, color_continuous_scale=plotly.colors.sequential.Blackbody)
        fig.update_layout(margin = dict(t=15, l=10, r=10, b=10), hoverlabel=dict(font_size=16, font_family="Rockwell"))
        fig.update_traces(hovertemplate=hover_sunburst_d)
    else:
        fig = px.sunburst(sub_df, values=sunburst_columns, path=["continent", "country"], template="plotly_dark",
                          color=sunburst_columns, color_continuous_scale=plotly.colors.sequential.Plotly3)
        fig.update_layout(margin = dict(t=15, l=10, r=10, b=10), hoverlabel=dict(font_size=16, font_family="Rockwell"))
        fig.update_traces(hovertemplate=hover_sunburst_rec)

    return fig

@app.callback(Output("treemap", "figure"),
            [Input("sunburst_columns", "value")])
def treemap(sunburst_columns):

    treemap_df = df_true.copy()
    treemap_df.drop([75,91,112,116,148,159,167,50,145], axis="index", inplace=True)
    treemap_df.reset_index(inplace=True)
    treemap_df.loc[171, "continent"] = "North America"
    treemap_df.loc[169, "continent"] = "Europe"
    tree_df = treemap_df.groupby(["country", "continent", "world"])[sunburst_columns].max().nlargest(25).reset_index()

    hover_treemap_con = "Country: %{label} <br>Confirmed Cases: %{value}</br>Tree Path: %{id}"
    hover_treemap_rec = "Country: %{label} <br>Recovered Cases: %{value}</br>Tree Path: %{id}"
    hover_treemap_d = "Country: %{label} <br>Deaths: %{value}</br>Tree Path: %{id}"

    if sunburst_columns=="confirmed":
        fig = px.treemap(tree_df, path=["world", "continent", "country"], values=sunburst_columns,
          color=sunburst_columns, template="plotly_dark", color_continuous_scale=px.colors.sequential.Jet)
        fig.update_layout(margin = dict(t=15, l=10, r=10, b=10),
                            hoverlabel=dict(font_size=16, font_family="Rockwell"))
        fig.update_traces(hovertemplate=hover_treemap_con)
    elif sunburst_columns=="recovered":
        fig = px.treemap(tree_df, path=["world", "continent", "country"], values=sunburst_columns,
          color=sunburst_columns, template="plotly_dark", color_continuous_scale=px.colors.sequential.Rainbow)
        fig.update_layout(margin = dict(t=15, l=10, r=10, b=10),
                            hoverlabel=dict(font_size=16, font_family="Rockwell"))
        fig.update_traces(hovertemplate=hover_treemap_rec)
    else:
        fig = px.treemap(tree_df, path=["world", "continent", "country"], values=sunburst_columns,
          color=sunburst_columns, template="plotly_dark", color_continuous_scale=px.colors.sequential.Turbo)
        fig.update_layout(margin = dict(t=15, l=10, r=10, b=10),
                            hoverlabel=dict(font_size=16, font_family="Rockwell"))
        fig.update_traces(hovertemplate=hover_treemap_d)

    return fig

@app.callback(Output("ortho_earth", "figure"),
            [Input("ortho_id", "value")])
def make_orthographic_chart(ortho_id):
    
    hover_earth = "Country: %{label} <br>%{value} </br>"
    fig = px.choropleth(df_true, locations="country", locationmode="country names", color=ortho_id, 
                    color_continuous_scale="Turbo",
                     projection="natural earth", template="plotly_dark")
    fig.update_geos(
        resolution=50,
        showcoastlines=True, coastlinecolor="RebeccaPurple",
        showland=True, landcolor="LightGreen",
        showocean=True, oceancolor="LightBlue",
        showlakes=True, lakecolor="Blue",
        showrivers=True, rivercolor="Blue"
    )

    fig.update_traces(hovertemplate=hover_earth)
    fig.update_geos(projection_type="orthographic")
    fig.update_layout(margin={"r":0,"t":20,"l":0,"b":20},
                        hoverlabel=dict(bgcolor="#2d2d2d", font_size=16, font_family="Rockwell"))

    return fig

@app.callback(Output("animated_choro", "figure"),
             [Input("my-date-picker-range", "start_date"),
             Input("my-date-picker-range", "end_date")])
def choropleth(start_date, end_date):
    
    new_df = confirmed[(confirmed["date"]>=start_date) & (confirmed["date"]<=end_date)]
    
    fig = px.choropleth(new_df, locations="country", locationmode="country names",
                      color_continuous_scale="Jet", color="confirmed", animation_frame="new_date_str", 
                      projection="robinson", template="plotly_dark")

    #fig.update_layout(margin={"r":0,"t":40,"l":40,"b":0})
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 5
    
    return fig


if __name__ == "__main__":
    app.run_server(dev_tools_hot_reload=False)