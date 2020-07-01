This project seeks to implement an investment strategy using several important investment principles developed in Daniel Weagley's Finance and Investments course at Georgia Tech. The text underlying these principles are found in Andrew Ang's Asset Management text.

The theory is to rebalance a portfolio of 70% equities to 30% bonds, split evenly between corporate bonds (ticker: VTC) and government bonds (ticker: BND). This allocation of a 70/30% split amounts to a risk aversion parameter of 2.0, which is moderately risk-averse. The optimal shares of equities for each ticker are determined by the highest Sharpe ratio portfolio and then the entire portfolio is then implemented automatically in Fidelity at the end of each month.

This task is divided into ten main parts:

# 1.1.  Collecting Current Portfolio Information from Fidelity
# 2.1.  Collecting Tickers to Use
# 3.1.  Combine Tickers into a Portfolio
4.1.  Obtain the Fama-French 5-Factors
4.2.  Obtain the Set of Returns for the Whole Universe
4.3.  Regress the Set of Returns to Fama-French 5-factors
5.1.  Forecast the Fama-French 5-Factors
6.1.  Estimate Returns From Forecast of Fama-French 5-Factors
7.1.  Forecast the Standard Deviation Using the GARCH Model
8.1.  Determine the Maximum Amount to Invest in Bonds
9.1.  Calculate the Mean-Variance Optimal Portfolio
9.2.  Determine the Optimal Number of Shares
10.1. Implement this Portoflio in Fidelity: Liquidate Portfolio
10.2. Implement this Portfolio in Fidelity: Buy Optimal Portfolio

### 1.1.  Collecting Current Portfolio Information from Fidelity

The current portfolio was obtained by using the Selenium module in Python to automate logging into Fidelity and scraping the webpage to obtain the current portfolio information as well as the current holdings. The current portfolio holdings are going to be used when executing trades and liquiding the portfolio. 

### 2.1.  Collecting Tickers to Use

The tickers used were scraped from the top weighted tickers chosen in five low-volatility ETF currently on the market. These ETFs are:

- State Street Global Advisers Low Volatility ETF (ONEV)
- ishares MSCI Minimum Volatility ETF (USMV)
- Vanguard U.S. Minimum Volatility ETF (VFMV)
- Invesco S&P 500 Low Volatility ETF (SPLV)
- Fidelity Low Volatility Factor ETF (FDLO)

These ticker weights are updated daily on each firm's website, and thus the top tickers can change day-to-day. Additionally, I picked a few tickers of my own to include, which vary based on my taste, etc.

### 3.1.  Combine Tickers into a Portfolio

Next, the tickers are all combined into one large portfolio, with a condition being each ticker in the combined portfolio must have been selected from more than one of the ETFs used in the analysis. This is done in order to ensure a more robust choice of tickers selected in the larger portfolio.

### 4.1.  Obtain the Fama-French 5-Factors

The Fama-French 5-Factors are a set of risk factors which explain to a very strong degree the risk premium present in equities. These 5-factors are:

- Rm - Rf : the market risk premium, which is the excess return on the market
- SMB : small minus big, which is the excess return of small stocks in comparison to big stocks
- HML : high book-to-market minus low book-to-market, which is a value investing strategy to purchase stocks with good book-to-market ratios.
- RMW : robust minus weak, which described the premium for robust operating portfolios minus weak operating portfolios
- CMA : conservative minus agressive, which describes the premium for conservative investment firms and agressive investment firms.
 
 These factors are provided by Eugene Fama's website, given by the [link](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html).

### 4.2.  Obtain the Set of Returns for the Whole Universe

The returns are obtained by the Yahoo Finance Python module, given by yfinance. This module scrapes Yahoo Finance for historical information based on the ticker. The returns are obtained daily for the past 30 months. This period of time was chosen to capture the essence of the returns, and this time frame produced better results in the ARIMA analysis.

### 4.3.  Regress the Set of Returns to Fama-French 5-factors

The set of returns are then regressed on the Fama-French 5-factors to obtain coefficients for the dependency of each stock on the 5 risk premium factors which make up the return.

### 5.1.  Forecast the Fama-French 5-Factors

Using an ARIMA (AutoRegressive Integrated Moving Average) analysis as a model for time-series forecasting, the Fama-French 5-factors are then estimated for the next month, from which the returns will be estimated. Factors are easier to estimate than returns.

### 6.1.  Estimate Returns From Forecast of Fama-French 5-Factors

Using the forecast of returns for the Fama-French 5-factors, the set of returns for tickers in the portfolio is estimated using the coefficients of each stock's dependency on the 5 risk premium factors which make up the return.

### 7.1.  Forecast the Standard Deviation Using the GARCH Model

Using the GARCH (Generalized AutoRegressive Conditional Heteroskedasticity) model, which was developed to estimate volatility in financial markets, the standard deviation of each stock in the portfolio can be estimated based on the past history of volatility for each return.

Additionally, the covariance between each stock pair is estimated by simply looking at the historical correlation between the tickers which make up the portfolio.

### 8.1.  Determine the Maximum Amount to Invest in Bonds

One of the core principles of this investment strategy is to automatically rebalance between an allocation of 70% for equities and 30% for bonds at the end of each month, or as near as possible to this percentage. Since shares can only be invested in integer amounts, there is some error in achieving the perfect allocation of 30% in bonds. Thus, to get as close as possible, the optimization solver Gurobi is used to calculed the optimal number of VTC and BND shares to buy to get as close as possible to a 30% weight in bonds, split evenly between corporate and government bonds.

### 9.1.  Calculate the Mean-Variance Optimal Portfolio

After the optimal number of bonds were chosen in 8.1 were chosen, the remaining portfolio is allocated to equities and is constructed as a constrained mean-variance optimized portfolio. The constraints are each weight for each asset much be between 1.0% and 20.0% of the equity portfolio. In order to effectively calculate a realistic optimal portfolio, the weights for each stock must lie between 1% and 20% of the equity portfolio. Additionally, each stock must have at least one share, unless the value of the share is such to exceed the 20% of the equity portoflio. The amount invested with the equity portfolio must lie between 97% and 103% of the equity portfolio value, which means the goal is for the entire equity portfolio to be invested. 

This optimization task is handled by the Guribi optimization software as a convex, integer optimization program. The number of shares in each asset can be optimized in various ways, and Gurobi is specially designed to handle this integer program. The problem is an integer program, because the number of shares must be an integer.

The Gurobi optimizer can then be run for several required minimum returns in order to create an efficient frontier. The efficient frontier contains a relationship between the expected return of the portfolio and the expected standard deviation of the portfolio; This is used in determining the optimal portfolio.

### 9.2.  Determine the Optimal Number of Shares

The optimal number of shares in each asset is given by a particular place on the efficient frontier, which corresponds to the highest ratio between the expected return and expected standard deviation. This optimal ratio is known as the maximum Sharpe Ratio, and shares are then traded based on this optimal portfolio.

### 10.1. Implement this Portoflio in Fidelity: Liquidate Portfolio

Since Fidelity does not have an API and the cookies required to effectively make http requests from Python are burdensome if not impossible to understand, the web driver Selenium can be used to automate the trade process in Fidelity. From 1.1, the current portfolio holdings are then entered into Fidelity as 'Sell' orders, which are automate and executed immediately.

### 10.2. Implement this Portfolio in Fidelity: Buy Optimal Portfolio

After the portfolio has been entirely liquidated, the optimal number of shares can then be automated in Fidelity with Selenium to generate the optimal portfolio. This portfolio is then rebalanced on the last trading day of each month, simply by calling the Python script to complete the analysis.
