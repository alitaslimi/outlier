# Outlier

The **[Outlier](https://outlier.streamlit.app)** is a data analytics tool that allows its users to conduct a cross-chain comparison of multiple blockchains on a wide variety of metrics. It is developed on top of **[Streamlit](https://streamlit.io)** by leveraging the free data of **[Flipside Crypto](https://flipsidecrypto.xyz)**.

## Structure

This tool is structured as a one-page web application. Users can filter their desired chart using the available options.

## Data

All of the data used for this tool are selected from the available free data on **[Flipside Crypto](https://flipsidecrypto.xyz)** and pulled using its REST API. The data for each metric is then saved on a CSV file in the **data** directory to improve the loading time.
