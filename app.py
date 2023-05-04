# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import PIL
from datetime import date, datetime, timedelta
from shroomdk import ShroomDK
from pathlib import Path

# Page Favicon
favicon = PIL.Image.open('favicon.png')

# Layout
st.set_page_config(page_title='Outlier - Blockchain Analytics', page_icon=favicon, layout='wide')

# Variables
theme_plotly = 'streamlit'
queries = pd.read_csv('data/queries.csv')
charts = pd.read_csv('data/charts.csv')

# Filters
c1, c2 = st.columns(2)
with c1:
    option_segments = st.selectbox(
        '**Segment**',
        options=queries['Segment'].unique(),
        key='option_segments'
    )

with c2:
    option_metrics = st.selectbox(
        '**Metric**',
        options=queries.query("Segment == @st.session_state.option_segments")['Metric'].unique(),
        key='option_metrics'
    )

option_blockchains = st.multiselect(
    '**Blockchains**',
    options=queries.query("Segment == @st.session_state.option_segments & Metric == @st.session_state.option_metrics")['Blockchain'].unique(),
    default=queries.query("Segment == @st.session_state.option_segments & Metric == @st.session_state.option_metrics")['Blockchain'].unique(),
    key='option_blockchains'
)

# Data
data_file = f"data/{st.session_state.option_segments.lower()}_daily_{st.session_state.option_metrics.lower().replace(' ', '_')}.csv"
df = pd.read_csv(data_file)

if df['Date'].iloc[0] >= str(date.today() - timedelta(2)):
    df = df.query("Blockchain == @st.session_state.option_blockchains")

else:
    pass
    API_KEY = st.secrets["API_KEY"]
    sdk = ShroomDK(API_KEY)

    dft = pd.DataFrame()
    for blockchain in st.session_state.option_blockchains:
        sql = Path(f"queries/{blockchain.lower()}_{st.session_state.option_segments.lower()}_daily_{st.session_state.option_metrics.lower().replace(' ', '_')}.sql").read_text()
        result_list = []
        for i in range(1,11):
            query_result = sdk.query(sql, page_size=100000, page_number=i)
            if query_result.run_stats.record_count == 0:  
                break
            else:
                result_list.append(query_result.records)
        result_df = pd.DataFrame()
        for idx, each_list in enumerate(result_list):
            if idx == 0:
                result_df = pd.json_normalize(each_list)
            else:
                result_df = pd.concat([dft, pd.json_normalize(each_list)])
        result_df['blockchain'] = blockchain
        dft = pd.concat([dft, result_df]).reset_index(drop=True)

    if dft.loc[dft['Date'] == dft['Date'].iloc[0], 'Blockchain'].unique().size < dft['Blockchain'].unique().size:
        dft.drop(dft[dft['date'] == dft['Date'].iloc[0]].index, inplace = True)

    if dft['Date'].iloc[0] > df['Date'].iloc[0]:
        df = pd.concat([dft[~dft.date.isin(df['Date'])], df], ignore_index=True)
        df.to_csv(data_file, index=False)

# Time Frame
option_dates = st.slider(
    '**Date Range**',
    min_value=datetime.strptime('2021-01-01', '%Y-%m-%d').date(),
    max_value=datetime.strptime(df['Date'].max(), '%Y-%m-%d').date(),
    value=(datetime.strptime('2023-01-01', '%Y-%m-%d').date(), datetime.strptime(df['Date'].max(), '%Y-%m-%d').date()),
    key='option_dates'
)

df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
df = df.query("Date >= @st.session_state.option_dates[0] & Date <= @st.session_state.option_dates[1]")

# Charts
title = charts.query("Segment == @st.session_state.option_segments & Metric == @st.session_state.option_metrics")['Title'].iloc[0]
y_axis = charts.query("Segment == @st.session_state.option_segments & Metric == @st.session_state.option_metrics")['Y Axis'].iloc[0]

fig = px.line(df, x='Date', y='Values', color='Blockchain', custom_data=['Blockchain'], title=f"{title} Over Time")
fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=y_axis, hovermode='x unified')
fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns([2, 1])
with c1:
    fig = go.Figure()
    for i in option_blockchains:
        fig.add_trace(go.Scatter(
            name=i,
            x=df.query("Blockchain == @i")['Date'],
            y=df.query("Blockchain == @i")['Values'],
            mode='lines',
            stackgroup='one',
            groupnorm='percent'
        ))
    fig.update_layout(title=f'Share of {title} Over Time')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='Values', names='Blockchain', title=f"Share of {title}")
    fig.update_layout(legend_title=None, legend_y=0.5)
    fig.update_traces(textinfo='percent+label', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)


# Whitespace
st.write("""
    #
    #
    #
""")

# Credits
c1, c2, c3 = st.columns(3)
with c1:
    st.info('**Data Analyst: [@AliTslm](https://twitter.com/AliTslm)**', icon="💡")
with c2:
    st.info('**GitHub: [@alitaslimi](https://github.com/alitaslimi)**', icon="💻")
with c3:
    st.info('**Data: [Flipside Crypto](https://flipsidecrypto.xyz)**', icon="🧠")