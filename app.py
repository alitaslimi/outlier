# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
from shroomdk import ShroomDK
from pathlib import Path
# import plotly.graph_objects as go
# import plotly.subplots as sp
# from PIL import Image
# import pathlib
# from bs4 import BeautifulSoup
# import logging
# import shutil
# import outlier

# Config
st.set_page_config(page_title='Outlier', page_icon=':bar_chart:', layout='wide')

# Global Variables
theme_plotly = 'streamlit' # None or streamlit
queries = pd.read_csv('data/queries.csv')
segments = queries['Segment'].unique()
metrics = queries.loc[queries['Segment'] == 'Transactions', 'Metric'].unique()
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Back-End
def get_data():
    data_file = f"data/{st.session_state.option_segments.lower()}_daily_{st.session_state.option_metrics.lower().replace(' ', '_')}.csv"
    df = pd.read_csv(data_file)

    if df['date'].iloc[0] == str(date.today() - timedelta(2)):
        print('up to date')
        return df
    
    else:
        print('not up to date')
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

date_range = pd.date_range(df['date'].min(), df['date'].max())
# datetime.strptime(df['date'].min(), '%m-%d-%Y').date()
# Filters
# option_dates = st.select_slider('**Date Range**', options=date_range, value=(df['date'].min(), df['date'].max()), key='option_dates')
option_dates = st.slider(
    '**Date Range**',
    min_value=datetime.strptime(df['date'].min(), '%Y-%m-%d').date(),
    max_value=datetime.strptime(df['date'].max(), '%Y-%m-%d').date(),
    value=(datetime.strptime(df['date'].min(), '%Y-%m-%d').date(), datetime.strptime(df['date'].max(), '%Y-%m-%d').date()),
    key='option_dates'
)

st.header("Daily Active Users")

    # print(queries.loc[queries['Segment'] == st.session_state.option_segments, 'Metric'].unique())
    # print(queries.query("Segment == @st.session_state.option_segments")['Metric'].unique())


    # Scale
    # option_scales = st.radio(
    #     '**Chart Scale**',
    #     options=['Linear', 'Log'],
    #     horizontal=True,
    #     key='option_scales'
    # )
    # test_x = (option_scales == 'Linear')
    # print(test_x)



# Content
# df = transactions_daily.query('Blockchain == @option_blockchains').sort_values(['Date', 'Transactions'], ascending=[False, False])
# fig = px.line(df, x='Date', y='Transactions', color='Blockchain', custom_data=['Blockchain'], title='Daily Total Transactions', markers=True)
# fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Transactions', hovermode='x unified')
# fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
# st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)


# df.query("date between @st.session_state.option_dates[0] and @st.session_state.option_dates[1]")

df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

df = df.query("date >= @st.session_state.option_dates[0] & date <= @st.session_state.option_dates[1]")

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
# st.divider()

# Credits
c1, c2, c3 = st.columns(3)
with c1:
    st.info('**Data Analyst: [@AliTslm](https://twitter.com/AliTslm)**', icon="💡")
with c2:
    st.info('**GitHub: [@alitaslimi](https://github.com/alitaslimi)**', icon="💻")
with c3:
    st.info('**Data: [Flipside Crypto](https://flipsidecrypto.xyz)**', icon="🧠")


# # Google Analytics
# def inject_ga():
#     GA_ID = "google_analytics"


#     GA_JS = """
#     <!-- Google tag (gtag.js) -->
#     <script async src="https://www.googletagmanager.com/gtag/js?id=G-PQ45JJR2R7"></script>
#     <script>
#     window.dataLayer = window.dataLayer || [];
#     function gtag(){dataLayer.push(arguments);}
#     gtag('js', new Date());

#     gtag('config', 'G-PQ45JJR2R7');
#     </script>
#     """

#     # Insert the script in the head tag of the static template inside your virtual
#     index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
#     logging.info(f'editing {index_path}')
#     soup = BeautifulSoup(index_path.read_text(), features="html.parser")
#     if not soup.find(id=GA_ID): 
#         bck_index = index_path.with_suffix('.bck')
#         if bck_index.exists():
#             shutil.copy(bck_index, index_path)  
#         else:
#             shutil.copy(index_path, bck_index)  
#         html = str(soup)
#         new_html = html.replace('<head>', '<head>\n' + GA_JS)
#         index_path.write_text(new_html)


# inject_ga()

# # Title
# st.title('Cross Chain Monitoring Tool')

# # Content
# c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14 = st.columns(14)
# c1.image(Image.open('images/ethereum-logo.png'))
# c2.image(Image.open('images/bsc-logo.png'))
# c3.image(Image.open('images/polygon-logo.png'))
# c4.image(Image.open('images/solana-logo.png'))
# c5.image(Image.open('images/avalanche-logo.png'))
# c6.image(Image.open('images/cosmos-logo.png'))
# c7.image(Image.open('images/near-logo.png'))
# c8.image(Image.open('images/flow-logo.png'))
# c9.image(Image.open('images/thorchain-logo.png'))
# c10.image(Image.open('images/osmosis-logo.png'))
# c11.image(Image.open('images/gnosis-logo.png'))
# c12.image(Image.open('images/optimism-logo.png'))
# c13.image(Image.open('images/arbitrum-logo.png'))
# c14.image(Image.open('images/axelar-logo.png'))

# st.write(
#     """
#     The crypto industry continues to progress and its development has never stopped. Contributors
#     of each blockchain keep developing each segment of the industry and the whole crypto ecosystem.
#     This tool is designed to allow viewers to journey into the world of crypto ecosystems of some
#     of the major blockchains, and compare their performance.

#     This tool is designed and structured in multiple **Pages** that are accessible using the sidebar.
#     Each of these Pages addresses a different segment of the crypto industry. Within each segment
#     (Macro, Transfers, Swaps, NFTs, etc.) you are able to filter your desired blockchains to
#     narrow/expand the comparison. By selecting a single blockchain, you can observe a deep dive
#     into that particular network.

#     All values for amounts, prices, and volumes are in **U.S. dollars** and the time frequency of the
#     analysis was limited to the last **30 days**.
#     """
# )

# st.subheader('Methodology')
# st.write(
#     """
#     The data for this cross-chain comparison were selected from the [**Flipside Crypto**](https://flipsidecrypto.xyz)
#     data platform by using its **REST API**. These queries are currently set to **re-run every 24 hours** to cover the latest
#     data and are imported as a JSON file directly to each page. The data were selected with a **1 day delay** for all
#     blockchains to be in sync with one another. The codes for this tool are saved and accessible in its 
#     [**GitHub Repository**](https://github.com/alitaslimi/cross-chain-monitoring).

#     It is worth mentioning that a considerable portion of the data used for this tool was manually decoded from the raw
#     transaction data on some of the blockchains. Besides that, the names of addresses, DEXs, collections, etc. are also
#     manually labeled. As the queries are updated on a daily basis to cover the most recent data, there is a chance
#     that viewers encounter inconsistent data through the app. Due to the heavy computational power required to execute
#     the queries, and also the size of the raw data being too large, it was not feasible to cover data for a longer period,
#     or by downloading the data and loading it from the repository itself. Therefore, the REST API was selected as the
#     proper form of loading data for the time being.
#     """
# )

# st.subheader('Future Works')
# st.write(
#     """
#     This tool is a work in progress and will continue to be developed moving forward. Adding other blockchains,
#     more KPIs and metrics, optimizing the code in general, enhancing the UI/UX of the tool, and more importantly,
#     improving the data pipeline by utilizing [**Flipside ShroomDK**](https://sdk.flipsidecrypto.xyz/shroomdk) are
#     among the top priorities for the development of this app. Feel free to share your feedback, suggestions, and
#     also critics with me.
#     """
# )