#%% 1.0 get modules

import os
import time
import pandas as pd
import scipy as sp
import numpy as np
from lxml import html
import requests as r
from zipfile import ZipFile
from io import BytesIO
import yfinance as yf
import statsmodels.api as sm
import gurobipy as grb
from functools import wraps
from pdb import set_trace as pb
from arch import arch_model
from matplotlib import pyplot as plt
from datetime import datetime
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

import warnings
warnings.filterwarnings('ignore')

###### ENTER YOUR INFORMATION ######

# personal information

optimalWeightAllocation = 0.70 # optimal allocation of stocks and bonds

# bond information

bonds = ['BND', 'VTC'] # bonds to use in the bond portfolio

# modifications

n = 20 # number of stocks to pick from each portfolio
additionalStocks = ['KL'] # additional stocks to include
highestAllocation = 0.20 # max weight to place on each stock
lowestAllocation = 0.01 # min weight to place on each stock
gamma = 1.0 # regularization parameter to spread 
    # out allocations in optimization

####################################

print(" Portfolio Optimization Strategy")
print(" Paul Sanders")
print(" Start 6.1.2020")
print(" ")

# %% 1.1 collect portfolio information from fidelity

print(" 1.1 Collect Current Portfolio Information from Fidelity")

# import username and password

file = open('/home/paul/Documents/TRADING STRATEGY/fidelityPassword.txt', 'r')
fileInfo = file.read().splitlines()

username = fileInfo[0].split(': ')[-1]
password = fileInfo[1].split(': ')[-1]

# keep the browser hidden

options = Options()
options.headless = True

# open up a browser tab

driver = webdriver.Firefox(options=options)

# get the portfolio information

def getFidelityPortfolioHoldings():

    # if the login is successful, loginKey will be True, otherwise False

    loginKey = False

    try:

        # open up fidelity's website

        driver.get(\
            'https://login.fidelity.com/ftgw/Fidelity/RtlCust/Login/Init')

        # sign-in with username and password

        webdriver.support.ui.WebDriverWait(driver,30)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, \
                'input#userId-input'))).send_keys(username)

        driver.find_element_by_css_selector(\
            'input#password').send_keys(password)
        driver.find_element_by_css_selector('button#fs-login-button').click()

        # navigate to the account positions page

        driver.get(\
            'https://oltx.fidelity.com/ftgw/fbc/oftop/portfolio#positions')

        # grab the current portfolio value from the account positions page

        elementPresent = EC.presence_of_element_located((By.CSS_SELECTOR, \
            '.account-selector--all-accounts-balance'))

        element = WebDriverWait(driver, 20).until(elementPresent)

        portfolioValue = float(element.text.split('$')[1].replace(',',''))

        # get the current holdings 

        portfolioHoldings = {'ticker':[], 'holdings':[]}

        # the holdings are found through the css selector,
        # which starts at index 5

        startingIndex = 5

        elementPresent = {}

        addToStartingIndex = 0

        getStocks = True

        # keep iterating as long as another holding is found
        # in the css selector

        while getStocks:
            
            index = startingIndex + addToStartingIndex

            try:

                # for the first holding,
                # make sure the webpage has finished loading

                if addToStartingIndex == 0:

                    elementPresent['ticker'] = \
                        EC.presence_of_element_located(\
                            (By.CSS_SELECTOR,tickerCSSSelector(index)))
                    elementPresent['holdings'] = \
                        EC.presence_of_element_located((By.CSS_SELECTOR,\
                            holdingsCSSSelector(index)))

                    ticker = WebDriverWait(driver, 20).until(\
                        elementPresent['ticker']).text
                    holdings = WebDriverWait(driver, 20).until(\
                        elementPresent['holdings']).text
                    holdings = int(float(holdings))

                else:

                    ticker = driver.find_element_by_css_selector(\
                        tickerCSSSelector(index)).text
                    holdings = driver.find_element_by_css_selector(\
                        holdingsCSSSelector(index)).text
                    holdings = int(float(holdings))

                portfolioHoldings['ticker'].append(ticker)
                portfolioHoldings['holdings'].append(holdings)

                addToStartingIndex += 2

            except:

                getStocks = False

                continue

        portfolioHoldings = pd.Series(
            portfolioHoldings['holdings'],
            index=portfolioHoldings['ticker'])

        loginKey = True

    except:

        portfolioValue = 'N/A'

        portfolioHoldings = 'N/A'

        loginKey = False

    return loginKey, portfolioValue, portfolioHoldings

# css selector definitions for getting portfolio holdings

def tickerCSSSelector(i):

    return 'tr.normal-row:nth-child('+str(i)+') > td:nth-child(1) > '\
        'div:nth-child(2) > a:nth-child(1) > '\
            'div:nth-child(1) > span:nth-child(1)'

def holdingsCSSSelector(i):

    return 'tr.normal-row:nth-child('+str(i)+') > td:nth-child(6)'

# grab the portfolio value if not provided

loginKey, portfolioValue, portfolioHoldings = getFidelityPortfolioHoldings()

# minimize the window

driver.close()

# if unsucessful in obtaining the portfolio value, then end program

if not loginKey:

    print(" Error: Unable to obtain the portfolio value."\
        "Please try again at another time.")

    exit()

# %% 2.1 scrape data from websites

print(" 2.1 Collect Tickers to Use")

# state street global advisers (ONEV)

website = "https://www.ssga.com/us/en/individual/etfs/library-content/"\
    "products/fund-data/etfs/us/holdings-daily-us-en-onev.xlsx"
fileData = pd.read_excel(website,header=4)

tickersSSGA = list(fileData["Ticker"][:n].values)

# ishares msci minimum volatility etf (USMV)

website = "https://www.ishares.com/us/products/239695/"\
    "ishares-msci-usa-minimum-volatility-etf/1467271812596.ajax?"\
    "fileType=csv&fileName=USMV_holdings&dataType=fund"
fileData = pd.read_csv(website,header=9)

tickersIShares = list(fileData["Ticker"][:n].values)

# vanguard u.s. minimum volatility etf (VFMV)

url = "http://api.vanguard.com/rs/ire/01/ind/fund/4419/"\
    "portfolio-holding/stock?start=1&count=500&asOfType=daily"

headers = {
    'Referer': 'http://api.vanguard.com/rs/ire/01/ind/fund/4419/'\
        'portfolio-holding/stock?start=1&count=500',
    'Accept' : 'application/json'
}

# sometimes the json response doesn't go through

def retry(times):

    def wrapper_fn(f):

        @wraps(f)
        def new_wrapper(*args,**kwargs):
            for _ in range(times):
                try:
                    return f(*args,**kwargs)
                except Exception as e:
                    error = e
            raise error

        return new_wrapper

    return wrapper_fn

@retry(3)
def getVanguardJson():
    
    response = r.get(url, headers=headers)

    j = response.json()

    tickersVanguard = [i["ticker"] for i in j['fund']['entity']][:n]

    return tickersVanguard

tickersVanguard = getVanguardJson()

# invesco s and p 500 low volatility etf (SPLV)

website = "https://www.invesco.com/us/financial-products/"\
    "etfs/holdings/main/holdings/0?audienceType=Investor"\
        "&ticker=SPLV&action=download"
fileData = pd.read_csv(website)

tickersInvesco = list(fileData.sort_values(by=["Weight"], ascending=False)\
    ["Holding Ticker"][:n].values)
tickersInvesco = [i.split() for i in tickersInvesco]
tickersInvesco = [i for j in tickersInvesco for i in j]

# fidelity low volatility factor etf (FDLO)

website = "https://research2.fidelity.com/fidelity/screeners/"\
    "etf/etfholdings.asp?symbol=FDLO&view=Holdings"
website2 = "https://research2.fidelity.com/fidelity/screeners/"\
    "etf/etfholdings.asp?symbol=FDLO&view=Holdings&page=1"

response = r.get(website).text
response = response + r.get(website2).text

tickersFidelity = []

index = 0
index2 = 0

while index < len(response):
    index = response.find("col-symbol", index)
    if index == -1:
        break
    index2 = response.find("/td", index)
    tickersFidelity.append(response[index+12:index2-1])
    index += 2
        
tickersFidelity = tickersFidelity[:n]

# first trust dorsey wright momentum and low volatility etf (DVOL)

website = "https://www.ftportfolios.com/Retail/"\
    "Etf/EtfHoldings.aspx?Ticker=DVOL"

response = r.get(website).text
response = "".join(response.split())
response = response.split("<td>")
response = [i.split("</td>") for i in response]

tickersFirstTrust = [i for j in response for i in j if i.isupper()][:-1][:n]

# %% 3.1. combine into a portfolio

print(" 3.1 Combine Tickers into a Portfolio")

# collect all tickers

tickers = tickersSSGA + tickersIShares + tickersVanguard + tickersInvesco \
    + tickersFidelity + tickersFirstTrust

# only include stocks which have been mentioned more than once

tickers = [tick for tick in tickers if tickers.count(tick)>1]

# add a few stocks of my own

tickers = tickers + additionalStocks

# remove duplicates

tickers = list(set(tickers))

tickers.sort()

# %% 4.1 obtain the fama-french 5-factors

print(" 4.1 Obtain the Fama-French 5-Factors")

website = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/"\
    "ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip"

response = r.get(website)

zipFile = ZipFile(BytesIO(response.content))
csvName = zipFile.namelist()[0]

file = zipFile.open(csvName)

famaData = pd.read_csv(file,header=2)

# change the column date format

famaData.columns.values[0] = 'DATE'

famaData['DATE'] = pd.to_datetime(famaData.iloc[:,0],\
    format='%Y%m',errors='coerce')

# due to the nature of the csv, drop na values

famaData = famaData.dropna()

# make the date column the index

famaData = famaData.set_index('DATE')

# convert the index values to the end of the month

famaData.index = famaData.index.to_period('M').to_timestamp('M')

# make sure all data values are floats

famaData = famaData.apply(pd.to_numeric)

# %% 4.2 obtain the set of returns for the whole universe

print(" 4.2 Obtain the Set of Returns for the Whole Universe")

# determine the starting date range

startDate = datetime.now() - pd.DateOffset(months=30)

# obtain the price of the stocks

# note: yfinance was throwing an issue with yf.download as of 6.28.2020
# used this workaround instead

priceStocks = pd.DataFrame()

for tick in tickers:
    while True:
        try:        
            priceStock = yf.Ticker(tick)
            priceStock = priceStock.history(start=startDate,progress=False)
        except:
            continue
        break  
    
    priceStocks[tick] = priceStock['Close'].dropna()

# obtain the current price of the bonds

# note: yfinance was throwing an issue with yf.download as of 6.28.2020
# used this workaround instead

currentPriceBonds = pd.DataFrame()

for bond in bonds:
    while True:
        try:        
            priceBond = yf.Ticker(bond)
            priceBond = priceBond.history(start=startDate,progress=False)
        except:
            continue
        break  
    
    currentPriceBonds[bond] = priceBond['Close'].dropna()

currentPriceBonds = currentPriceBonds.last('h')

# convert the price of the stocks to monthly data

priceMonthlyStocks = priceStocks.resample('1M').last()

# obtain the returns of the stocks

returnDailyStocks = priceStocks.rolling(2).apply(\
    lambda x: x[1] / x[0] - 1.0)
returnStocks = priceMonthlyStocks.rolling(2).apply(\
    lambda x: x[1] / x[0] - 1.0)

# %% 4.3 regress the set of returns to the fama-french 5-factors

print(" 4.3 Regress the Set of Returns to Fama-French 5-factors")

# prepare the data for regression

# merge the fama data and returns data

allVariables = returnStocks.join(famaData.iloc[:,:5]).dropna()

famaVariables = allVariables.iloc[:,-5:]

famaVariables = sm.add_constant(famaVariables)

returnVariables = allVariables.iloc[:,:-5]

# initialize the parameter array

modelParms = np.zeros(shape=(returnVariables.columns.shape[0],6))

# run the regression over all variables

for index,stk in enumerate(returnVariables.columns):

    model = sm.OLS(returnVariables.loc[:,stk], famaVariables)

    modelParms[index] = model.fit().params

# %% 5.1 roughly forcast the fama-french 5-factors

print(" 5.1 Forecast the Fama-French 5-Factors")

# shorted the amount of data used in the analysis

famaRecent = famaData[famaData.index > startDate]

# run the ARIMA analysis for each factor

famaEstimation = np.zeros(5)

forecastMonths = 1 + datetime.now().month \
    - famaData.index[-1].month

for var in range(5):

    # create the model

    # loop over p and q values to determine the best AIC value

    aicVal = []

    for p in range(4):
        for q in range(4):

            try:

                model = ARIMA(famaRecent.iloc[:,var], order=(p, 0, q))

                # fit the model

                fitted = model.fit()

                if p + q > 0:

                    aicVal.append(fitted.aic)

                    # check if it is the min

                    if min(aicVal) == fitted.aic:

                        pOpt = p
                        qOpt = q

            except:

                pass

    # use the optimal parameters

    model = ARIMA(famaRecent.iloc[:,var], order=(pOpt, 0, qOpt))

    # fit the model

    fitted = model.fit()

    fc, se, conf = fitted.forecast(forecastMonths, alpha=0.05)
    
    # forecast of the next month

    famaEstimation[var] = fc[-1]

# %% 6.1 use the estimation of fama-french 5-factors to predict returns

print(" 6.1 Estimate Returns from Forecast of Fama-French 5-Factors")

# using predicitons for the fama french factors, predict the return

returnPredictions = modelParms[:,0] + modelParms[:,1:].dot(famaEstimation)

# %% 7.1 calculate the rough standard deviation using the garch model

print(" 7.1 Forecast the Standard Deviation Using the Garch Model")

# initialize an array for standard deviation variables

nStocks = returnStocks.shape[1]

stdPredictions = np.zeros(nStocks)

# run the regression over all variables

for index,stk in enumerate(returnVariables.columns):

    # create the garch model

    returnStock = returnDailyStocks.iloc[:,index].dropna()

    garchModel = arch_model(returnStock)

    # fit the garch model

    fitGarch = garchModel.fit(disp='off')

    # grab the forecasted standard deviation each day for the next 20 days

    stdGarchVals = np.sqrt(fitGarch.forecast(horizon=22).variance).iloc[-1,:]

    # convert the standard deviation to monthly standard deviation

    stdGarch = stdGarchVals.mean() * np.sqrt(22)

    # append to the array

    stdPredictions[index] = stdGarch

# determine the correlation matrix

corPredictions = returnStocks.corr()

# calculate the covariance matrix

covPredictions = np.diag(stdPredictions).dot(corPredictions)\
    .dot(np.diag(stdPredictions))

# %% 8.1 determine the maximum amount to invest in bonds

print(" 8.1 Determine the Maximum Amount to Invest in Bonds")

# calculate the maximum amount available to invest in equities

amountBonds = (1-optimalWeightAllocation)*portfolioValue

# calculate a lower bound on the number of bond shares

bondSharesLowerBound = np.floor(amountBonds / currentPriceBonds \
    / currentPriceBonds.shape[1])

# gurobi model

m = grb.Model('bond allocation')

# add variables

bondNames = currentPriceBonds.columns.values

numberOfShares = {}

for bnd in range(bondNames.shape[0]):

    # grab the lower bound

    lowerBound = bondSharesLowerBound.iloc[:,bnd]
    
    # define the variable for each bond

    numberOfShares[bnd+1] = m.addVar(lb=lowerBound, \
        vtype=grb.GRB.INTEGER, \
        name='numberOfShares['+bondNames[bnd]+']')

errorTerm = m.addVar(name='errorTerm')

m.update()

# add objective by minimizing the difference in the amount to invest in bonds
 
m.setObjective(errorTerm, grb.GRB.MINIMIZE)

m.update()

# add constraints

m.addConstr(errorTerm >= \
    np.array(list(numberOfShares.values())).dot(\
        currentPriceBonds.values[0].T)- amountBonds)

m.addConstr(errorTerm >= amountBonds - np.array(list(\
    numberOfShares.values())).dot(currentPriceBonds.values[0].T))

m.update()

# run the optimization

m.optimize()

# grab the optimal number of shares in each bond

bondShares = m.getVars()[:-1]
bondShares = pd.Series([i.x for i in bondShares],\
    index=bondNames)

# determine the maximum amount available to invest in equities

maxInvestibleEquities = \
    portfolioValue - bondShares.dot(currentPriceBonds.T)[0]

# %% 9.1 calculate the mean-variance optimal portfolio

print(" 9.1 Calculate the Mean-Variance Optimal Portfolio")

# create the efficient frontier array

nRuns = 20

desiredMinimumReturns = np.linspace(0.010,0.060,num=nRuns)

stdVals = []

retVals = []

# determine the highest sharpe ratios

shrpRatio = []

equityShares = []

# grab the current stock price

currentStockPrice = priceStocks.iloc[-1]

# determine the maximum amount available for each stock

upperBounds = np.floor( \
    highestAllocation*maxInvestibleEquities / currentStockPrice)

lowerBounds = np.ceil( \
    lowestAllocation*maxInvestibleEquities / currentStockPrice)

# ensure the lower bound is not greater than the upper bound

lowerBounds = pd.Series(\
    [min(index) for index in zip(upperBounds, lowerBounds)],\
        index = upperBounds.index)

# iterate over minimum return values to generate the efficient frontier

for minRet in desiredMinimumReturns:

    # gurobi model

    m = grb.Model("portfolio optimization")

    # add variables

    stockNames = returnStocks.columns.values

    numberOfShares = {}

    for stk in range(nStocks):

        numberOfShares[stk+1] = \
            m.addVar(lb=lowerBounds.iloc[stk],\
                        ub=upperBounds.iloc[stk],\
                        vtype=grb.GRB.INTEGER,\
                        name='numberOfShares['+stockNames[stk]+']')

    m.update()

    # determine weights in the objective functions

    shareValues = np.diag(list(numberOfShares.values())).dot(\
        currentStockPrice)

    weights = shareValues / maxInvestibleEquities

    # add objective by minimizing variance portfolio

    regParameter = gamma*weights.dot(weights)

    obj = weights.T.dot(covPredictions).dot(weights) \
        + regParameter

    m.setObjective(obj, grb.GRB.MINIMIZE)

    m.update()

    # add constraint of weights must be within tolerance

    m.addConstr(np.sum(shareValues) <= maxInvestibleEquities * 1.00,\
        name='must not invest over the maximum threshold')

    m.addConstr(np.sum(shareValues) >= maxInvestibleEquities * 0.99,\
        name='must invest over the minimum threshold')

    m.update()

    # add constraint of a minimum return obtained

    m.addConstr(weights.dot(returnPredictions) >= minRet, \
        name='minimum return condition')

    m.update()

    # run the optimization

    m.optimize()

    # only continue if the optimizer was successful,
    # which is a status code of 2

    if m.Status == 2:

        # get the optimal number of shares

        equityShare = [i.x for i in m.getVars()]

        equityShares.append(equityShare)

        # determine the return

        weights = np.diag(equityShare).dot(currentStockPrice)

        weights = weights / np.sum(weights)

        ret = weights.dot(returnPredictions)

        retVals.append(ret)

        # determine the standard deviation

        std = np.sqrt(weights.dot(covPredictions).dot(weights))

        stdVals.append(std)

        # determine the sharpe ratio

        shrpRatio.append(ret / std)

# %% 9.2 get the optimal number of shares based on the optimal sharpe ratio

print(" 9.2 Determine the Optimal Number of Shares")

# determine the optimal number of shares

equityShares = pd.Series(
    equityShares[np.array(shrpRatio).argmax()],
    index=pd.Index(stockNames))

allShares = equityShares.append(bondShares)

print("")
print(" The optimal allocation is:")
print(" BONDS:")

print(bondShares)

print(" EQUITIES:")

print(equityShares)

# %% 10.1 implement this automatically in Fidelity : liquidate portfolio

print(" 10.1 Implement this Portfolio in Fidelity: Liquidate Portfolio")
print(" Now implementing the sell orders in Fidelity:")

# keep the browser hidden

options = Options()
options.headless = False

# open up a browser tab

driver = webdriver.Firefox(options=options)

# open up fidelity's website

driver.get('https://login.fidelity.com/ftgw/Fidelity/RtlCust/Login/Init')

# sign-in with username and password

webdriver.support.ui.WebDriverWait(driver,30)\
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, \
        'input#userId-input'))).send_keys(username)

driver.find_element_by_css_selector('input#password').send_keys(password)
driver.find_element_by_css_selector('button#fs-login-button').click()

# navigate to the account positions page

driver.get('https://oltx.fidelity.com/ftgw/fbc/oftop/portfolio#positions')

# open up the trade screen

time.sleep(5)

driver.find_element_by_css_selector('.trade').click()

# excecute a trade

def trade(ticker, amount, actionType):

    time.sleep(5)

    driver.find_element_by_css_selector('#qt-symbol').send_keys(ticker)

    action = Select(driver.find_element_by_css_selector(\
        '#st-form-container--action'))

    action.select_by_visible_text(actionType)

    driver.find_element_by_css_selector('#st-form-container--quantity')\
        .send_keys(amount)

    orderType = Select(driver.find_element_by_css_selector(\
        '#st-form-container--order-type'))

    orderType.select_by_visible_text('Market Order')

    driver.find_element_by_css_selector('#previewTrade').click()

    time.sleep(3)

    driver.find_element_by_css_selector('#placeOrder').click()

    time.sleep(3)

    driver.find_element_by_css_selector('#fttNewTicketButton').click()

    return True

# calculate the number of shares to sell

sharesToSell = pd.concat(
    [portfolioHoldings,allShares],axis=1).fillna(0.0)
sharesToSell = sharesToSell.iloc[:,0] - sharesToSell.iloc[:,1]

# liquidate portfolio

for tick,holding in enumerate(sharesToSell):

    if holding > 0.0:

        trade(sharesToSell.index[tick], int(holding), 'Sell')

        print(" {0:5} shares of {1:5} sold".format(
            holding, sharesToSell.index[tick]))

# %% 10.2 implement this automatically in Fidelity : buy optimal portfolio

print(" 10.2 Implement this Portfolio in Fidelity: Buy Optimal Portfolio")
print(" Now implementing the trades in Fidelity:")

# calculate the number of shares to buy

sharesToBuy = -sharesToSell

# rebalance portfolio

for tick,holding in enumerate(sharesToBuy):

    if holding > 0.0:
    
        trade(sharesToBuy.index[tick], int(holding), 'Buy')

        print(" {0:5} shares of {1:5} buy".format(
            holding, sharesToBuy.index[tick]))

print(" FINISHED")