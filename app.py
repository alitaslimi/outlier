# ------------------------------ Libraries ------------------------------ #

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta

# ------------------------------ Configuration ------------------------------ #

st.set_page_config(page_title='Outlier - Blockchain Analytics', page_icon=':sparkles:', layout='wide')

# ------------------------------ Filters ------------------------------ #

# Variables
charts = pd.read_csv('data/charts.csv')
queries = pd.read_csv('data/queries.csv')

# Filter Segment, Metric, and Aggregation
c1, c2, c3 = st.columns(3)
with c1:
    option_segments = st.selectbox(
        label='**Segment**',
        options=charts['Segment'].unique(),
        key='option_segments'
    )
with c2:
    option_metrics = st.selectbox(
        label='**Metric**',
        options=charts.query("Segment == @option_segments")['Metric'].unique(),
        key='option_metrics'
    )
with c3:
    option_aggregation = st.selectbox(
        label='**Aggregation**',
        options=charts.query("Segment == @option_segments & Metric == @option_metrics")['Aggregation'].unique(),
        key='option_aggregation'
    )

# Filter Blockchains
option_blockchains = st.multiselect(
    label='**Blockchains**',
    options=queries.query("Segment == @option_segments & Metric == @option_metrics & Aggregation == @option_aggregation")['Blockchain'].unique(),
    default=queries.query("Segment == @option_segments & Metric == @option_metrics & Aggregation == @option_aggregation")['Blockchain'].unique(),
    key='option_blockchains'
)

# Data Source
# Load the local data file using the filters
data_file = f"data/{option_segments.lower()}_{option_metrics.lower().replace(' ', '_')}_{option_aggregation.lower()}_daily.csv"
df = pd.read_csv(data_file)

# Check whether the data is up to date or not, the time difference is currently 1 day
# If the data is up to date, the local loaded file will be filtered using the selected blockchains
if df['Date'].iloc[0] >= str(date.today() - timedelta(1)) and df.loc[df['Date'] == df['Date'].iloc[0], 'Blockchain'].unique().size == df['Blockchain'].unique().size:
    df = df.query("Blockchain == @option_blockchains")

# If the data is not up to date, the data will be pulled online using their subsequent query ID
# Currently, only the free data on Flipside are being used for this tool
# The queries are broken down into multiple small SQLs that get the data for each blockchain separately
# This helps to considerably reduce the required computational power to run each query
# The result of each query is loaded as a JSON into a data frame
# Then the updated rows will be added to the locally loaded data file
# And saves it as a CSV file for the next iterations
else:
    query_result = pd.DataFrame()
    for blockchain in option_blockchains:
        if df[df['Blockchain'] == blockchain]['Date'].iloc[0] < str(date.today() - timedelta(1)):
            query_id = queries.query("Segment == @option_segments & Metric == @option_metrics & Blockchain == @blockchain & Aggregation == @option_aggregation")['Query'].iloc[0]
            query_result = pd.read_json(f"https://api.flipsidecrypto.com/api/v2/queries/{query_id}/data/latest")
            query_result['Blockchain'] = blockchain
            query_result['Date'] = query_result['Date'].dt.strftime('%Y-%m-%d')
            df = pd.concat([query_result[~query_result['Date'].isin(df[df['Blockchain'] == blockchain]['Date'])], df]).sort_values(['Date', 'Blockchain'], ascending=[False, True]).reset_index(drop=True)

    df.to_csv(data_file, index=False)

# Date Alignment
# Removes the last date if it only contains a portion of blockchains instead of all of them
if df.loc[df['Date'] == df['Date'].iloc[0], 'Blockchain'].unique().size < df['Blockchain'].unique().size:
    df.drop(df[df['Date'] == df['Date'].iloc[0]].index, inplace = True)

# Filter Aggregation
if option_aggregation != 'Blockchain':
    option_aggregates = st.multiselect(
        label=f"**{option_aggregation}s**",
        options=df[option_aggregation].unique(),
        default=df[option_aggregation].head(5).unique(),
        max_selections=20,
        help="It is advised to select as few items as possible to prevent the charts from being clustered. Max selection is 20.",
        key='option_aggregates'
    )

# Filter Chart Scale And Date Range
c1, c2 = st.columns([1, 7])
with c1:
    option_scale = st.radio('**Scale**', options=['Linear', 'Log'], key='option_scale')
with c2:
    option_dates = st.slider(
        '**Date Range**',
        min_value=datetime.strptime(df['Date'].min(), '%Y-%m-%d').date(),
        max_value=datetime.strptime(df['Date'].max(), '%Y-%m-%d').date(),
        value=(datetime.strptime(str(date.today() - timedelta(90)), '%Y-%m-%d').date(), datetime.strptime(df['Date'].max(), '%Y-%m-%d').date()),
        key='option_dates'
    )

# Divider
st.divider()

# ------------------------------ Visualization ------------------------------ #

# Chart Theme
theme_plotly = 'streamlit'

# Week days for the heatmap chart
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Metric Description
metric_descrption = charts.query("Segment == @option_segments & Metric == @option_metrics & Aggregation == @option_aggregation")['Description'].iloc[0]
st.info(f"**Metric Description**: {metric_descrption}", icon="💡")

# Apply the blockchains and date filters to the data frame
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
df = df.query("Blockchain == @option_blockchains & Date >= @option_dates[0] & Date <= @option_dates[1]").reset_index(drop=True)

# Apply the aggregates filter to the data frame
series = option_aggregation
if option_aggregation != 'Blockchain':
    if len(option_aggregates) > 1:
        df = df.query(f"{option_aggregation} == {option_aggregates}").groupby(['Date', option_aggregation]).agg('sum').reset_index()
    else:
        series = 'Blockchain'
        df = df.query(f"{option_aggregation} == {option_aggregates}").groupby(['Date', 'Blockchain']).agg('sum').reset_index()

# Checks whether the minimum number of blockchains is selected or not
# Currently, the limit is at least 2 blockchains
if len(option_blockchains) < 2:
    st.warning('Please select at least 2 blockchains to see the metrics.')

# Plotly Charts
else:
    # Get the chart details from the charts.csv file
    title = charts.query("Segment == @option_segments & Metric == @option_metrics & Aggregation == @option_aggregation")['Title'].iloc[0]
    yaxis = charts.query("Segment == @option_segments & Metric == @option_metrics & Aggregation == @option_aggregation")['Y Axis'].iloc[0]
    unit = charts.query("Segment == @option_segments & Metric == @option_metrics & Aggregation == @option_aggregation")['Unit'].fillna('').iloc[0]
    decimals = charts.query("Segment == @option_segments & Metric == @option_metrics & Aggregation == @option_aggregation")['Decimals'].iloc[0]

    # Plot the data using a Plotly line chart
    df = df.sort_values(['Date', 'Values'], ascending=[False, False]).reset_index(drop=True)
    fig = px.line(df, x='Date', y='Values', color=series, custom_data=[series], title=f"Daily {title}", log_y=(option_scale == 'Log'))
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=yaxis, hovermode='x unified')
    fig.update_traces(hovertemplate=f"%{{customdata}}: {unit}%{{y:,.{decimals}f}}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    # Plot the normalized data using a Plotly area chart
    normalized_chart = charts.query("Segment == @option_segments & Metric == @option_metrics & Aggregation == @option_aggregation")['Normalized'].iloc[0]
    if normalized_chart:
        fig = go.Figure()
        for i in df['Blockchain'].unique() if option_aggregation == 'Blockchain' else df[option_aggregation].unique():
            fig.add_trace(go.Scatter(
                name=i,
                x=df.query(f"{option_aggregation} == @i")['Date'],
                y=df.query(f"{option_aggregation} == @i")['Values'],
                customdata=df.query(f"{option_aggregation} == @i")[option_aggregation],
                mode='lines',
                stackgroup='one',
                groupnorm='percent',
                hovertemplate="%{customdata}: %{y:,.1f}%<extra></extra>"
            ))
        fig.update_layout(title=f'Daily Share of {title}', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    # View and download the data in a CSV format
    with st.expander('**View and Download Data**'):
        column_values = f"{option_segments} {option_metrics}"
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        df = df.sort_values(['Date', 'Values'], ascending=[False, False]).reset_index(drop=True)
        df = df.rename(columns={'Values': column_values})
        df = df[['Date', option_aggregation, column_values]]
        df.index += 1
        st.dataframe(df, use_container_width=True)
        st.download_button(
            label="Download CSV",
            data=df.to_csv().encode('utf-8'),
            file_name=f"outlier_{option_segments.lower()}_{option_metrics.lower().replace(' ', '_')}_{option_aggregation}_daily.csv",
            mime='text/csv',
        )

# Divider
st.divider()

# ------------------------------ Credits ------------------------------ #

c1, c2, c3 = st.columns(3)
with c1:
    st.info('**Data Analyst: [@AliTslm](https://twitter.com/AliTslm)**', icon="💡")
with c2:
    st.info('**GitHub: [@alitaslimi](https://github.com/alitaslimi)**', icon="💻")
with c3:
    st.info('**Data: [Flipside Crypto](https://flipsidecrypto.xyz)**', icon="🧠")