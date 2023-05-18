# Outlier

The **[Outlier](https://outlier.streamlit.app)** is a blockchain analytics tool that allows its users to perform a cross-chain comparison between various blockchains on a wide variety of metrics. It is developed on top of **[Streamlit](https://streamlit.io)** by leveraging the free data of **[Flipside Crypto](https://flipsidecrypto.xyz)**.

## Structure

This tool is structured as a one-page web application. Users can filter their desired chart using the available options.

## Data

All of the data used for this tool are selected from the available free data on **[Flipside Crypto](https://flipsidecrypto.xyz)** and pulled using its REST API. The data for each metric is then saved on a CSV file in the **data** directory to improve the loading time.

# Upcoming Features
Here is the list of upcoming features that will be added to the app. The list items are formatted with the following pattern: **Segment, Metric, Aggregation, Blockchain**.
- Queries
  - Addresses, Active Users, Blockchain, Flow
- Charts
 - Blocks, Block Time, Blockchain
 - Fees, Total Gas Used, Blockchain
 - Fees, Average Gas Used, Blockchain
 - Fees, Median Gas Used, Blockchain
 - Fees, Average Gas Price, Blockchain
 - Fees, Median Gas Price, Blockchain
 - Fees, Base Fee per Gas, Blockchain
 - NFTs, Traded NFTs, Blockchain
 - NFTs, Traded Collections, Blockchain
 - NFTs, Sales Count, Marketplace
 - NFTs, Buyers, Marketplace
 - NFTs, Traded NFTs, Marketplace
 - NFTs, Traded NFTs, Marketplace
