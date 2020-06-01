This project seeks to analyze the distance to default (DD) and probability of default (PD) of publicly-traded companies for year year from 1970-2015. The goal is to see how the DD and PD change from each year to the next and how these to measures related to the overall health of the economy. This is given by various financial stress indices, such as the NBER Recession Index, Moody's BAA-Fed Fund Spread, and the Cleveland Financial Stress Index. 

In calculating the DD and PD, there are three main methods, with each method being more accurate and more complex. The three methods are the naive, the direct, and the iterative method, which will be explained in more detail.

Thus, this task is divided into six parts: 

1. Downloading the Data
2. Calculating the DD and PD with the Naive Method
3. Calculating the DD and PD with the Direct Method
4. Calculating the DD and PD with the Indirect Method
5. Comparison of the Methods
6. Comparison with Financial Stress Indices

### 1. Downloading the Data

There were a few main sources of data used for this project:
  
a. DSF : The daily stock returns and volume, along with shares outstanding, were obtained by analyzing the DSF SAS file which was obtained through the QCF server. This data file had company information in the form of the CUSIP number and was used to obtain the share price, the return from the previous year, number of shares, and the volatility of the firm's equity value.

b. FUNDA : This company-specific data information file contained information on the outstanding debt held by each company and the link between CUSIP and the CIK number. This was used with DSF in order to calculate the distance to default. 
  
c. DAILYFED : This dataset contained the 3-month treasury bond yield, which was used as the risk-free interest rate, This risk-free rate was then used in methods 2 and 3 to calculate the distance to default.
  
d. NBER Recession Data : This information regarding recessions contains two values: 0 to indicate an expansionary period, and 1 to indicate a recessionary period. The link is here: [NBER Recession Data](https://research.stlouisfed.org/fred2/series/USREC).

e. Moody's BAA-Fed Fund Spread : This data file contains the spread between BAA Corporate Bond yields and the Fed Funds rate. When in a recessionary period, this spread tends to be high, because the BAA Corporate Bond yields are closely linked to the probability of default for firms in this same riskiness level. The link is here: [Moody's BAA-Fed Fund Spread](https://fred.stlouisfed.org/series/BAAFFM).

f. Cleveland Financial Stress Index : This dataset is similarly a gauge of the financial stress in the US financial system, with a high score indicating significant stress, and a low score indicates a low-stress period. However, it needs to be takes with a degree of cautions, because as the authors note themselves, the calculation of this index contains errors. The link is here: [Cleveland Financial Stress Index](https://fred.stlouisfed.org/series/CFSI).

In actually scraping and extracting the data, the SAS Software was used in order to prepare the data. SAS was necessary in order to deal with the sheer size of the DSF and FUNDA dataset would make it infeasable for direct analysis in the R Statistical Package.

### 2. Calculating the DD and the PD with the Naive Method

The naive method calculates the distance to default (DD) as:

<p align="center">
  <img height='70' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/2calc1.png">
</p>

where

<p align="center">
  <img height='70' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/2calc2.png">
</p>

Here,

- E is the firm's market capitalization (equity) value
- F is the firm's value of debt
- T represents the time period of one year
- <img height='15' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/2calc4.png"> represents the volatility of the firm's market capitalization E over the past year.
- <img height='15' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/2calc3.png"> represents the volatility of the firm's assets over the past year using the naive method.

Now, from these calculations, and according to the Black-Scholes theory we can calculate the PD as 

<p align="center">
  <img height='70' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/2calc5.png">
</p>

In order to calculate these values over the range from 1970-2015, 200 firms were randomly selected from each year. This was done in an effort to lower the computational strain while still capturing the essence of the calculations.

We can compute the descriptive statistics over the entire sample period for the DD and PD given by:

| --- | Distance to Default (DD) | Probability of Default (PD) | 
| Number of Observations	| 9195 |	9195 |
| Minimum	| -4.691 |	0.000 |
| 25th Percentile	| 5.082 |	0.000 |
| 50th Percentile	| 8.775 |	0.000 |
| Mean	| inf |	0.0109 |
| 75th Percentile	| 14.562 |	0.000 |
| Maximum	| inf |	0.999 |
| Standard Deviation	| N/A |	0.0589 |

Additionally, we can compare the descriptive statistics across time. However, in many occurrences the debt of a firm is zero, making the distance to default effectively zero and throwing off the descriptive statistics for distance to default. Thus, it is more convenient to plot the PD instead. The mean, 25th, 50th, and 75th percentiles for PD across time is given by:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/2graph1.png">
</p>

with the standard deviation given by:

<p align="center">
  <img height='400' src="https://raw.githubusercontent.com/physics-paul/mfi-assignment5/master/images/2graph2.png">
</p>

The calculation was completed in the R Markdown file 'defaultCalculation.r' under the section 'Naive Sentiment Analysis' header.

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
