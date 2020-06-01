This project seeks to implement an investment strategy using several important investment principles developed in Daniel Weagley's Finance and Investments course at Georgia Tech.

This task is divided into six parts:

1. Collecting the tickers to use
2. Predict the returns for next month
3. Predict the standard deviation for next month
4. Calculate the optimal portfolio
5. Invest automatically in Fidelity

### 1. Collecting the tickers to use

The tickers used were scraped from the top weighted tickers chosen in five low-volatility ETF currently on the market. These ETFs are:

- State Street Global Advisers Low Volatility ETF (ONEV)
- ishares MSCI Minimum Volatility ETF (USMV)
- Vanguard U.S. Minimum Volatility ETF (VFMV)
- Invesco S&P 500 Low Volatility ETF (SPLV)
- Fidelity Low Volatility Factor ETF (FDLO)

These ticker weights are updated daily on each firm's website, and thus the top tickers can change day-to-day. Additionally, I picked a few tickers of my own to include.

### 2. Predict the returns for next month

Once the tickers were obtained, then the historical adjusted closing price was obtained throught Yahoo Finance's API


### 3. Calculating the DD and the PD with the Direct Method

The direct method calculates the distance to default (DD) by treating the market capitalization E as an option on the firm's assets with strike price F, the company's debt. In the Black-Scholes theory, this equation is given by:

<p align="center">
  <img height='50' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc1.png">
</p>

where

<p align="center">
  <img height='80' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc3.png">
</p>

and 

<p align="center">
  <img height='40' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc4.png">
</p>

Here,

<p align="center">
  <img height='80' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc2.png">
</p>

is the cumulative normal distribution. Now, the volatility of the firm's market capitalization can be measured as a funciton of the volatilty in the firm's assets, and it is given by:

<p align="center">
  <img height='80' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc5.png">
</p>

At this point, we know:

- E is the firm's market capitalization (equity) value
- F is the firm's value of debt
- T represents the time period of one year
- <img height='15' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/2calc4.png"> represents the volatility of the firm's market capitalization E over the past year.

To highlight, we don't know V, the firm's assets, and <img height='15' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc6.png">, the volatility of the firm's assets. These two things we can directly solve for, because we have two equations and two unknowns. The distance of default, <img height='15' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc7.png">, can then be calculated. Additionally, we can calculate the probability of default, which is simply the cumulative normal distribution integrated to an upper bound of the distance to default. Given before, this value is:

<p align="center">
  <img height='80' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc2.png">
</p>

Using the same range of data as in the naive method, for the direct method, we can compute the descriptive statistics over the entire sample period for the DD and PD given by:

| --- | Distance to Default (DD) | Probability of Default (PD) | 
| Number of Observations	| 9195 |	9195 |
| Minimum	| -5.728 |	0.000 |
| 25th Percentile	| 3.073 |	0.000 |
| 50th Percentile	| 5.565 |	0.000 |
| Mean	| inf |	0.0262 |
| 75th Percentile	| 10.245 |	0.001 |
| Maximum	| inf |	0.999 |
| Standard Deviation	| N/A |	0.101 |

Additionally, we can compare the descriptive statistics across time. The mean, 25th, 50th, and 75th percentiles for the PD across time is given by:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3graph1.png">
</p>

with the standard deviation given by:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3graph2.png">
</p>

The calculation was completed in the R Markdown file 'defaultCalculation.r' under the section 'Direct Sentiment Analysis' header.

### 4. Calculating the DD and the PD with the Indirect Method

Both of the previous methods, the naive method and the direct method, calculate the volatility by directly solving for it. This method takes a different approach: 

- First, guess a value for the volatility of the firm's assets for the previous year.

- Second, using the equity option equation (and the guess of the volatility parameter), calculate the daily value of the firm's assets.

- Third, estimate the volatility of these daily values of the firm's assets.

- Repeat with the new value of the firm's volatility until <img height='15' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc6.png"> converges.

Thus, we can calculate V, the firm's assets, and <img height='15' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/3calc6.png">, the volatility of the firm's assets, for every year for every firm sampled.

Using the same range of data as in the naive and direct method, for the indirect method, we can compute the descriptive statistics over the entire sample period for the DD and PD given by:


| --- | Distance to Default (DD) | Probability of Default (PD) | 
| Number of Observations	| 9195 |	9195 |
| Minimum	| -10.414 |	0.000 |
| 25th Percentile	| 5.726 |	0.000 |
| 50th Percentile	| 13.501 |	0.000 |
| Mean	| inf |	0.0332 |
| 75th Percentile	| 31.306 |	0.001 |
| Maximum	| inf |	0.999 |
| Standard Deviation	| N/A |	0.135 |

Additionally, we can compare the descriptive statistics across time. The mean, 25th, 50th, and 75th percentiles for the PD and across time is given by:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/4graph1.png">
</p>

with the standard deviation given by:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/4graph2.png">
</p>

The calculation was completed in the R Markdown file 'defaultCalculation.r' under the section 'Indirect Sentiment Analysis' header.

### 5. Comparison of the Methods

At this point, we can compare all three methods, by looking at the correlation across the mean DD value throughout the years. This correlation for the mean of the probability to default, PD, is given in the following table:

| --- | Naive Method | Direct Method | Indirect Method |
| Naive Method	| 1.000 |	0.815 | 0.673 |
| Direct Method	| 0.815 |	1.000 | 0.763 |
| Indirect Method	| 0.673 |	0.763 | 1.000 |

Graphically, we can represent this correlation by looking at the mean of the methods across time:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/5graph1.png">
</p>

### 6. Comparison with Financial Stress Indices

For the rest of this analsis, the distance to default will be calculated by the mean value for each year using the direct method. This DD will will be compared to financial stress indices.

When comparing the NBER Recession data with the calculation of the DD, the resulting plot yields:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/6graph1.png">
</p>

Additionally, the plot of the Moody's BAA-Fed Fund Spread with the DD looks like:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/6graph2.png">
</p>

Lastly, we can compare our calculations to the Cleveland Financial Stress Index, we obtain the result:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/6graph3.png">
</p>

Interestingly, we see a strong correlation between the distance to default (DD), the probability of default (PD), and current economic conditions, confirming the expected result firms are more likely to default in difficult economic times.
