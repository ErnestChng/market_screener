import datetime as dt
from typing import List

import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si

yf.pdr_override()

"""
https://towardsdatascience.com/making-a-stock-screener-with-python-4f591b198261
https://algotrading101.com/learn/yahoo-finance-api-guide/
"""


class StockScreener:
    """
    Stock Screener object.
    """

    def __init__(self, index_ticker: str, stock_list: List[str]) -> None:
        """
        Constructor for the Stock Screener object.

        :param index_ticker: String representing the ticker for the index
        :param stock_list: List of Strings representing the stocks in the index
        """
        self.index_ticker = index_ticker
        self.stock_list = stock_list

        self.end_date = dt.datetime.now()
        self.start_date = self.end_date - dt.timedelta(days=365)

        self.stocks_of_interest = []

    def get_index_return(self) -> float:
        """
        Gets the returns of the index. Used for calculations for RS ratings.

        :return: Float representing the returns of the index
        """
        print(f"\npulling {self.index_ticker}")
        index_df = pdr.get_data_yahoo(self.index_ticker, start=self.start_date, end=self.end_date)
        index_df['percent_change'] = index_df['Adj Close'].pct_change()

        return index_df['percent_change'].sum() * 100

    @staticmethod
    def get_rs_rating(df: pd.DataFrame, index_return: float) -> float:
        """
        Gets the RS ratings.

        :param df: DataFrame representing the stock
        :param index_return: Float representing the returns of the index
        :return: Float representing the RS ratings
        """
        assert 'Adj Close' in df.columns, 'column Adj Close is missing from dataframe!'

        df['percent_change'] = df['Adj Close'].pct_change()
        stock_return = df['percent_change'].sum() * 100

        return round((stock_return / index_return) * 10, 2)

    @staticmethod
    def get_current_close(df: pd.DataFrame) -> float:
        """
        Gets the current adjusted closing price of the stock.

        :param df: DataFrame representing the stock
        :return: Float representing the Adjusted Closing Price
        """
        return df['Adj Close'][-1]

    @staticmethod
    def get_sma_50(df: pd.DataFrame) -> float:
        """
        Gets the latest value of the 50 Day Simple Moving Average of the stock.

        :param df: DataFrame representing the stock
        :return: Float representing the 50 Day SMA
        """
        df['sma_50'] = round(df.iloc[:, 4].rolling(window=50).mean(), 2)

        return df['sma_50'][-1]

    @staticmethod
    def get_sma_150(df: pd.DataFrame) -> float:
        """
        Gets the latest value of the 150 Day Simple Moving Average of the stock.

        :param df: DataFrame representing the stock
        :return: Float representing the latest value of the 150 Day SMA
        """
        df['sma_150'] = round(df.iloc[:, 4].rolling(window=150).mean(), 2)

        return df['sma_150'][-1]

    @staticmethod
    def get_sma_200(df: pd.DataFrame) -> float:
        """
        Gets the latest value of the 200 Day Simple Moving Average of the stock

        :param df: DataFrame representing the stock
        :return: Float representing the latest value of the 200 Day SMA
        """
        df['sma_200'] = round(df.iloc[:, 4].rolling(window=200).mean(), 2)

        return df['sma_200'][-1]

    @staticmethod
    def get_sma_200_20(df: pd.DataFrame) -> float:
        """
        Gets the previous 1 month value of the 200 Day Simple Moving Average of the stock.

        :param df: DataFrame representing the stock
        :return: Float representing the previous 1 month value of the 200 Day SMA
        """
        return df['sma_200'][-20]

    @staticmethod
    def get_low_52_week(df: pd.DataFrame) -> float:
        """
        Gets the 52 week low price.

        :param df: DataFrame representing the stock
        :return: Float representing the 52 week low price
        """
        return min(df['Adj Close'][-260:])

    @staticmethod
    def get_high_52_week(df: pd.DataFrame) -> float:
        """
        Gets the 52 week high price

        :param df: DataFrame representing the stock
        :return: Float representing the 52 week high price
        """
        return max(df['Adj Close'][-260:])

    def get_stocks(self) -> pd.DataFrame:
        """
        Screens the stocks and selects based on 8 conditions.

        Condition 1: Current Price > 150 SMA and > 200 SMA
        Condition 2: 150 SMA and > 200 SMA
        Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
        Condition 4: 50 SMA > 150 SMA and 50 SMA > 200 SMA
        Condition 5: Current Price > 50 SMA
        Condition 6: Current Price is at least 30% above 52 week low (many of the best are up to 100-300% before coming out of consolidation)
        Condition 7: Current Price is within 25% of 52 week high
        Condition 8: IBD RS rating is greater than 70

        :return: DataFrame representing the selected stocks
        """
        print('Beginning screening process...\n')
        len_stock_list = len(self.stock_list)

        index_return = self.get_index_return()  # used for RS rating

        for counter, stock in enumerate(self.stock_list):
            try:
                print(f"\npulling {stock} with index {counter}/{len_stock_list}")
                df = pdr.get_data_yahoo(stock, start=self.start_date, end=self.end_date)

                rs_rating = self.get_rs_rating(df, index_return)
                current_close = self.get_current_close(df)
                sma_50 = self.get_sma_50(df)
                sma_150 = self.get_sma_150(df)
                sma_200 = self.get_sma_200(df)
                low_52_week = self.get_low_52_week(df)
                high_52_week = self.get_high_52_week(df)

                sma_200_20 = self.get_sma_200_20(df)

                condition_1 = current_close > sma_150 > sma_200
                condition_2 = sma_150 > sma_200
                condition_3 = sma_200 > sma_200_20
                condition_4 = sma_50 > sma_150 > sma_200
                condition_5 = current_close > sma_50
                condition_6 = current_close >= 1.3 * low_52_week
                condition_7 = current_close >= (0.75 * high_52_week)
                condition_8 = rs_rating >= 70

                if condition_1 and condition_2 and condition_3 and condition_4 and condition_5 and condition_6 and condition_7 and condition_8:
                    self.stocks_of_interest.append({
                        'Date': self.end_date,
                        'Counter': counter,
                        'Ticker': stock,
                        'RS Rating': rs_rating,
                        'Current Close': current_close,
                        '50 Day MA': sma_50,
                        '150 Day MA': sma_150,
                        '200 Day MA': sma_200,
                        '52 Week Low': low_52_week,
                        '52 Week High': high_52_week
                    })

                    print(f"{stock} match the requirements")

            except Exception as e:
                print(e)
                print(f"An error occurred while pulling data for {stock}")

        print('\nScreening completed!')
        return pd.DataFrame(self.stocks_of_interest)


if __name__ == '__main__':
    index_ticker = '^GSPC'
    stock_list = si.tickers_sp500()
    sc = StockScreener(index_ticker, stock_list)

    df_interest = sc.get_stocks()
    print(df_interest)

    df_interest.to_csv(f'screened_stocks.csv', index=False)
