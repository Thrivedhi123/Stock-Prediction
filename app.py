import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import numpy as np
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

st.title("Stock Dashboard")

Ticker = st.sidebar.text_input('Ticker', 'AAPL')  # Default ticker
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

if Ticker and start_date and end_date:
    try:
        # Download stock data
        data = yf.download(Ticker, start=start_date, end=end_date)

        if data.empty:
            st.error("No data found. Please check the Ticker symbol or date range.")
        else:
            st.write("Stock Data:")
            st.dataframe(data)
            
            # Ensure 'Adj Close' is 1-dimensional
            adj_close = data['Adj Close'].squeeze()
            
            # Create the plot
            fig = px.line(
                data_frame=data,
                x=data.index,
                y=adj_close,
                title=f"{Ticker} Adjusted Closing Prices"
            )
            st.plotly_chart(fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.warning("Please provide valid inputs for Ticker, Start Date, and End Date.")

pricing_data,fundamental_data,news=st.tabs(["Pricing Data","Fundamental Data","News"])
with pricing_data:
    st.header("Pricing Movements")
    data2=data
    
    data2['% Change']=data['Adj Close']/data['Adj Close'].shift(1)-1
    data2.dropna(inplace=True)
    st.write(data2)
    annual_return = data2['% Change'].mean()*252*100
    st.write("Annual Returns are",annual_return,"%")
    stdev = np.std(data2['% Change'])*np.sqrt(252)
    st.write("The Standard Deviation is",stdev*100,'%')
    st.write('Risk Adj.return',annual_return/(stdev*100),'%')
    
with fundamental_data:
    key = 'JE94E9YCCD90287T'
    fd = FundamentalData(key,output_format='pandas')
    st.subheader('Balance Sheet')
    balance_sheet = fd.get_balance_sheet_annual(Ticker)[0]
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)
    
    st.subheader('Income Statement')
    income = fd.get_income_statement_annual(Ticker)[0]
    is1 = income.T[2:]
    is1.columns = list(income.T.iloc[0])
    st.write(is1)
    
    st.subheader('Cash Flow Statement')
    csff = fd.get_cash_flow_annual(Ticker)[0]
    cs = csff.T[2:]
    cs.columns = list(csff.T.iloc[0])
    st.write(cs)
    st.write()
    
with news:
    st.header(f'News of {Ticker}')
    sn = StockNews(Ticker,save_news=False)
    df_news = sn.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['summary'][i])
        st.write('Title Sentiment ',df_news['sentiment_title'][i])
        st.write('News Sentiment',df_news['sentiment_summary'][i])
