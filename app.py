# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import PIL
from datetime import date, datetime, timedelta

# Page Favicon
favicon = PIL.Image.open('favicon.png')

# Layout
st.set_page_config(page_title='Outlier - Blockchain Analytics', page_icon=favicon, layout='wide')

# Variables
theme_plotly = 'streamlit'
queries = pd.read_csv('data/queries.csv')
charts = pd.read_csv('data/charts.csv')
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# App Description
with st.expander('**How It Works?**'):
    st.write("""
        Lorem ipsum
    """)

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
        options=queries.query("Segment == @option_segments")['Metric'].unique(),
        key='option_metrics'
    )

option_blockchains = st.multiselect(
    '**Blockchains**',
    options=queries.query("Segment == @option_segments & Metric == @option_metrics")['Blockchain'].unique(),
    default=queries.query("Segment == @option_segments & Metric == @option_metrics")['Blockchain'].unique(),
    key='option_blockchains'
)

# Data
data_file = f"data/{option_segments.lower()}_{option_metrics.lower().replace(' ', '_')}_daily.csv"
df = pd.read_csv(data_file)

if df['Date'].iloc[0] >= str(date.today() - timedelta(1)) and df.loc[df['Date'] == df['Date'].iloc[0], 'Blockchain'].unique().size == df['Blockchain'].unique().size:
    df = df.query("Blockchain == @option_blockchains")

else:
    query_result = pd.DataFrame()
    for blockchain in option_blockchains:
        if df[df['Blockchain'] == blockchain]['Date'].iloc[0] < str(date.today() - timedelta(2)):
            query_id = queries.query("Segment == @option_segments & Metric == @option_metrics & Blockchain == @blockchain")['Query'].iloc[0]
            query_result = pd.read_json(f"https://api.flipsidecrypto.com/api/v2/queries/{query_id}/data/latest")
            query_result['Blockchain'] = blockchain
            query_result['Date'] = query_result['Date'].dt.strftime('%Y-%m-%d')
            df = pd.concat([query_result[~query_result['Date'].isin(df[df['Blockchain'] == blockchain]['Date'])], df]).sort_values(['Date', 'Blockchain'], ascending=[False, True]).reset_index(drop=True)

    df.to_csv(data_file, index=False)

if df.loc[df['Date'] == df['Date'].iloc[0], 'Blockchain'].unique().size < df['Blockchain'].unique().size:
    df.drop(df[df['Date'] == df['Date'].iloc[0]].index, inplace = True)

# Time Frame
option_dates = st.slider(
    '**Date Range**',
    min_value=datetime.strptime(df['Date'].min(), '%Y-%m-%d').date(),
    max_value=datetime.strptime(df['Date'].max(), '%Y-%m-%d').date(),
    value=(datetime.strptime(str(date.today() - timedelta(90)), '%Y-%m-%d').date(), datetime.strptime(df['Date'].max(), '%Y-%m-%d').date()),
    key='option_dates'
)

# Metric Description

metric_descrption = charts.query("Segment == @option_segments & Metric == @option_metrics")['Description'].iloc[0]
# st.write("""
#         @chart_descrption
#     """)
st.info(f"**Metric Description**: {metric_descrption}", icon="💡")

df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
df = df.query("Blockchain == @option_blockchains & Date >= @option_dates[0] & Date <= @option_dates[1]")

# Charts
if len(option_blockchains) <= 1:
    st.warning('Please select at least 2 blockchains to see the metrics.')

else:
    title = charts.query("Segment == @st.session_state.option_segments & Metric == @st.session_state.option_metrics")['Title'].iloc[0]
    y_axis = charts.query("Segment == @st.session_state.option_segments & Metric == @st.session_state.option_metrics")['Y Axis'].iloc[0]

    fig = px.line(df, x='Date', y='Values', color='Blockchain', custom_data=['Blockchain'], title=f"{title} Over Time")
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=y_axis, hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

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

    df_heatmap = df.copy()
    df_heatmap['Normalized'] = df.groupby('Blockchain')['Values'].transform(lambda x: (x - x.min()) / (x.max() - x.min()))
    fig = px.density_heatmap(df_heatmap, x='Blockchain', y=df_heatmap.Date.dt.strftime('%A'), z='Normalized', histfunc='avg', title=f"Heatmap of Normalized {title}")
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, coloraxis_colorbar=dict(title='Normalized'))
    fig.update_xaxes(categoryorder='category ascending')
    fig.update_yaxes(categoryorder='array', categoryarray=week_days)
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