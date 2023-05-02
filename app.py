# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
from shroomdk import ShroomDK
from pathlib import Path

# Config
st.set_page_config(page_title='Outlier', page_icon=':bar_chart:', layout='wide')

# Global Variables
theme_plotly = 'streamlit' # None or streamlit
queries = pd.read_csv('data/charts.csv')
segments = queries['Segment'].unique()
metrics = queries.loc[queries['Segment'] == 'Transactions', 'Metric'].unique()
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Back-End
def get_data():
    data_file = f"data/{st.session_state.option_segments.lower()}_daily_{st.session_state.option_metrics.lower().replace(' ', '_')}.csv"
    df = pd.read_csv(data_file)

    if df['date'].iloc[0] >= str(date.today() - timedelta(2)):
        return df.query("blockchain == @st.session_state.option_blockchains")
    
    else:
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

        if dft.loc[dft['date'] == dft['date'].iloc[0], 'blockchain'].unique().size < dft['blockchain'].unique().size:
            dft.drop(dft[dft['date'] == dft['date'].iloc[0]].index, inplace = True)

        if dft['date'].iloc[0] > df['date'].iloc[0]:
            df = pd.concat([dft[~dft.date.isin(df['date'])], df], ignore_index=True)
            df.to_csv(data_file, index=False)

    return df

# Sidebar
with st.sidebar:
    # Segments
    option_segments = st.selectbox(
        '**Segment**',
        options=segments,
        key='option_segments'
    )

    # Metrics
    option_metrics = st.selectbox(
        '**Metric**',
        options=queries.query("Segment == @st.session_state.option_segments")['Metric'].unique(),
        key='option_metrics'
    )

    # Blockchains
    option_blockchains = st.multiselect(
        '**Blockchains**',
        options=queries.query("Segment == @st.session_state.option_segments & Metric == @st.session_state.option_metrics")['Blockchain'].unique(),
        default=queries.query("Segment == @st.session_state.option_segments & Metric == @st.session_state.option_metrics")['Blockchain'].unique(),
        key='option_blockchains'
    )

# Content
df = get_data()

# Filters
option_dates = st.slider(
    '**Date Range**',
    min_value=datetime.strptime('2021-01-01', '%Y-%m-%d').date(),
    max_value=datetime.strptime(df['date'].max(), '%Y-%m-%d').date(),
    value=(datetime.strptime('2023-01-01', '%Y-%m-%d').date(), datetime.strptime(df['date'].max(), '%Y-%m-%d').date()),
    key='option_dates'
)

df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
df = df.query("date >= @st.session_state.option_dates[0] & date <= @st.session_state.option_dates[1]")

# Chart
fig = px.line(df, x='date', y=df[df.columns[1]], color='blockchain', custom_data=['blockchain'])
fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=df.columns[1], hovermode='x unified')
fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
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