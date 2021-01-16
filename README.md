# Market Screener

Simple personal project to screen stocks/crypto to pursue my interest in finance.

## Stocks Screener

Inspired from https://towardsdatascience.com/making-a-stock-screener-with-python-4f591b198261.

Automates the process of screening stocks from a list (i.e. S&P500, Nasdaq, DJI) and helps to select stocks based on 8
pre-defined conditions (see below)

- Condition 1: Current Price > 150 SMA and > 200 SMA
- Condition 2: 150 SMA and > 200 SMA
- Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
- Condition 4: 50 SMA > 150 SMA and 50 SMA > 200 SMA
- Condition 5: Current Price > 50 SMA
- Condition 6: Current Price is at least 30% above 52-week low (many of the best are up to 100-300% before coming out of
  consolidation)
- Condition 7: Current Price is within 25% of 52-week high
- Condition 8: IBD RS rating is greater than 70

## Crypto Screener

*Note: WIP*
