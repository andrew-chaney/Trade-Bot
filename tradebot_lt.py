# Ultimate goal is a slow, but steady, stream of income. Target strategy is buying when the 50-day SMA is above the 200-day SMA for any given stock. 
# Stop loss is never over 20% for a given stock, and you should never lose more than 2% of your overall portfolio value due to the decline of a single stock.
# Take profit is set so that every 40% increase in value for a stock you sell 20% of your shares in that stock.

import time, copy
import pandas as pd
import pandas_ta as ta
import datetime
from math import ceil, floor
from config import *
import alpaca_trade_api as tradeapi

BASE_URL = "https://paper-api.alpaca.markets"
api = tradeapi.REST(API_KEY, API_SECRET_KEY, BASE_URL)



###############################################################################
################################# FUNCTIONS ###################################
###############################################################################

# Pull historical data from the API
# Collecting daily intervals for SMAs... ensure that the data is the most recent date
def get_historical_data(symbol, interval="1D", limit=200):

    # Initialize counter for data request attempts
    attempts = 1

    # Loop to get data
    while True:
        # Make initial attempt at getting the data
        try:
            # Organize in Pandas DataFrame
            r = api.get_barset(symbol, interval, limit).df

        # If you can't pull the data push an error message and take a break
        except Exception as e:
            print("ERROR: Could not check to see if the data is updated.")
            print(str(e))
            time.sleep(5)

        # Check to see if the data is up to date, from today.
        try:
            # Get the last updated time from the dataset
            lastDate = r.last("1D").index[0]
            # Convert to UTC
            lastDate = lastDate.tz_convert('utc').date()
            # Get Current Time in UTC
            currentDate = datetime.datetime.utcnow().date()
            # Compare the difference
            difference = int((currentDate - lastDate).days)
            # Compare to the interval to ensure it is up to date
            if difference < 1:
                # If checks are good return the dataset
                print(f"Data load successful for interval {interval}.")
                return r

            else:
                # Keep requesting unless you've reached the attempt limit
                if 10 >= attempts >= 5:
                    print("------------------------------------------------")
                    print(f"Trying to fetch new data... Attempt: {attempts}.")
                    print(f"Current Date: {currentDate}")
                    print(f"Last Update: {lastDate}")
                    print(f"Days Since Last Update: {difference} days")
                    print(f"Set Data Update Interval: {interval}")
                    print("------------------------------------------------")


                # If you have reaching the max attempts, break the loop so that
                # the next stock can be examined.
                elif attempts > 10:
                    return pd.DataFrame({'A' : []})


                # Take a break before looping again
                time.sleep(5)
                attempts += 1


        # If you can't pull the data push an error message and take a break
        except Exception as e:
            print("ERROR: Could not check to see if the data is updated.")
            print(str(e))
            time.sleep(5)

            if attempts > 10:
                return pd.DataFrame({'A' : []})
            attempts += 1



# Get any historical data: FOR PROGRAMMING AND TRAINING ONLY
def any_historical_data(symbol, interval='1D', limit=200):
    # Grab data from API and organize into Pandas DataFrame
    r = api.get_barset(symbol, interval, limit).df

    # Return organized data
    return r



# Get the most recent price of a stock
def most_recent_price(symbol):
    # Pull a single most recent price from the API
    r = get_historical_data(symbol, '1Min', limit=1)

    v = r[symbol]['close'].values

    price = v[0]

    return float(price)



# Return whether or not the market is open
def market_status():
    r = api.get_clock().is_open

    return r



# Return how long until the market will open next
def time_to_open():
    # Find the current time
    current_time = datetime.datetime.utcnow()
    # If it is Monday - Thurday
    if current_time.weekday() <= 4:
        d = (current_time + datetime.timedelta(days=1)).date()
    else:
        days_to_mon = 0 - current_time.weekday() + 7
        d = (current_time + datetime.timedelta(days=days_to_mon))
    next_day = datetime.datetime.combine(d, datetime.time(13, 30))
    seconds = (next_day - current_time).total_seconds()
    return round(seconds)



# Quantity of a stock that you can purchase
def quantity_available(symbol, stocks_owned):
    # How much is in your account?
    amt = (float(api.get_account().cash) / float(5 - stocks_owned))
    # How much does the stock cost per share?
    cost = most_recent_price(symbol)
    #cost = float(cost)
    # Calculate how many shares you can buy
    shares = amt / cost
    # Round down to a whole share number
    qty = floor(shares)
    # Return the number of shares to buy
    return qty


# Visual aid to announce an order that has been submitted.
def announce_order():
    print('#\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t #')
    print('#\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t #')
    print('#\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t #')
    print('#    O R D E R   S U B M I T T E D    #')
    print('#\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t #')
    print('#\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t #')
    print('#\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t #')



def total_portfolio_value():
    return float(api.get_account().equity)



def currentPrice(data):
    return float(data['close'].values[-1])



def takeProfit(take_profit_counter, price_bought, current_price):
    print("### TAKE PROFIT FUNCTION ###")
    print(f"Current Price: ${round(current_price, 2)}")
    print(f"Price Bought: ${round(float(price_bought), 2)}")
    percentGain = current_price / float(price_bought)
    if current_price < float(price_bought):
        print(f"Percent Gain: -{round(percentGain, 2)}%")
    else:
        print(f"Percent Gain: {round(percentGain, 2)}%")
    # Convert float to a whole number percentage
    percentGain = (percentGain - 1) * 100
    if (percentGain > 40) and (floor(percentGain / 40) > take_profit_counter):
        return True
    else:
        return False



def stopLoss(priceHigh, current_price, price_bought, amount_owned):
    print("### STOP LOSS FUNCTION ###")
    print(f"High Price: ${round(priceHigh, 2)}")
    print(f"Current Price: ${round(current_price, 2)}")
    priceDelta = priceHigh - current_price
    portVal = total_portfolio_value()
    print(f"Difference Between High and Current Prices: -${priceDelta}")

    if current_price < priceHigh:
        print(f"Difference Percentage of Total Portfolio Value: - {round(((amount_owned * priceDelta) / portVal), 2)}%")

    if float((amount_owned * priceDelta) / portVal) > 0.02:
        return True
    elif current_price <= (float(price_bought) * 0.9):
        return True
    else:
        return False



#######################################################################
####################### INDICATOR FUNCTION TEST #######################
#######################################################################

# Return Simple Moving Average for periods 9, 50, and 200.
def sma(data, stock):
    sma9 = ta.sma(data['close'], length=50)
    sma50 = ta.sma(data['close'], length=50).values[-1]
    sma200 = ta.sma(data['close'], length=200).values[-1]

    print(f"SMA50: {sma50}")
    print(f"SMA200: {sma200}")
    print(f"Current SMA9: {sma9.values[-1]}")
    print(f"SMA9 Yesterday: {sma9.values[-2]}")
    print(f"SMA9 Two-Days Ago: {sma9.values[-3]}")

    # Test 1 is if the SMA50 is over the SMA200.
    test1 = False
    # Test 2 is if the current SMA9 is greater than the previous 2 SMA9s.
    test2 = False

    if sma50 > sma200:
        test1 = True
    
    if sma9.values[-1] > sma9.values[-2] and sma9.values[-1] > sma9.values[-3]:
        test2 = True

    if test1 and test2:
        return True
        
    else:
        return False

    

########################################################################
########################### BUY AND SELL ###############################
########################################################################

# Buy a stock
def buy(symbol, stocks_owned): 
    # Show visual cue that we are ordering something and to pay attention
    # for the details.
    announce_order()

    side = 'buy' # we are buying
    qty = quantity_available(symbol, stocks_owned)# how many shares can you get
    time_in_force = 'gtc' # order is good until cancelled
    price = most_recent_price(symbol)

    # Initialize attempt counter
    attempt = 0
    while attempt < 5:
        try:
            api.submit_order(
                symbol = symbol,
                qty = qty,
                side = side,
                type = 'market',
                time_in_force = time_in_force,
            )
            print(f"Market order submitted to buy {qty} shares of {symbol} at ${price}")
            print(f"Total Cost: ${price*qty}")
            print(f"Initial Take Profit: ${price * 1.4}")
            print()
            return True

        except Exception as e:
            print(f"WARNING_EO: order of | {qty} {symbol} {side} | did not enter")
            print(e)
            time.sleep(5)
            attempt += 1

    print(f"WARNING_SO: Could not submit the order, aborting (buy({symbol}))")
    return price

# Sell a certain percentage of stock you own
def sell(symbol, percentage=1):
    announce_order() 

    side = 'sell' # we are buying
    amt_owned = abs(int(api.get_position(symbol).qty)) # how many shares have to sell
    qty = ceil(amt_owned * percentage)
    time_in_force = 'gtc' # order is good until cancelled
    price = most_recent_price(symbol)

    # Initialize attempt counter
    attempt = 0
    while attempt < 5:
        try:
            api.submit_order(
                symbol = symbol,
                qty = qty,
                side = side,
                type = 'market',
                time_in_force = time_in_force
            )
            print(f"Market order submitted to sell {qty} shares of {symbol} {price}.")
            print(f"Total Value: ${price*qty}")
            print()
            return True

        except Exception as e:
            print(f"WARNING_EO: order of | {qty} {symbol} {side} | did not enter")
            print(e)
            time.sleep(5)
            attempt += 1

    print(f"WARNING_SO: Could not submit the order, aborting (sell({symbol}))")
    return False



########################################################################
############################### MAIN CODE ##############################
########################################################################

def run_bot():
    # Run the bot non-stop

    # A list of stocks
    stocks = ['TSLA', 'MSFT', 'SPY', 'AMD', 'AAPL', 'PLUG', 'NVDA', 'SPT', 'AMZN', 'PTON', 'ISRG', 'TWLO', 'PRPL', 'GRWG', 'VALE', 'WKHS', 'FB', 'DIS', 'NFLX', 'BABA', 'DKNG', 'SPCE', 'GME', 'ICLN', 'NKE', 'LMT', 'BLK', 'SNE', 'UBER', 'AEP', 'ERIC', 'MCHP', 'APTV', 'ETSY', 'KEYS', 'LH', 'TCOM', 'HUBS', 'GNRC', 'FSLY', 'APHA', 'INSG', 'SE', 'APPS', 'BLNK', 'DOCU', 'CGC', 'TDOC', 'SNAP', 'GOOGL', 'NKLA', 'PLL', 'RTX', 'LI', 'NIO', 'KIRK', 'ZM', 'FVRR', 'TRIL', 'NLS', 'PRTS', 'QDEL', 'DQ', 'BTAI', 'AWH', 'SITM', 'ENPH', 'ARCT', 'OSTK', 'CRDF', 'KSPN', 'IMVT', 'RUN', 'CELH', 'PRPH', 'EXPI', 'NGD', 'PACB', 'CMBM', 'SEDG', 'GLG', 'TWST', 'IMAB', 'REGI', 'OIIM', 'PINS', 'GSHD', 'GRVY', 'JKS', 'BAND', 'FSM', 'NET', 'VAPO', 'BNTX', 'SAM', 'STKL', 'TRVN', 'DSKE', 'SWBI', 'AMRC', 'PNTG', 'FLGT', 'DRD', 'AHCO', 'BWMX', 'CARR', 'SAVA', 'SWTX', 'FTCH', 'CRNC', 'ACMR', 'GSX', 'FUTU', 'NOVA', 'TTD', 'NFE', 'ZS', 'CALX', 'PSNL', 'PDEX', 'KROS', 'FATE', 'DNLI', 'FIVN', 'OTRK', 'SUMR', 'AVXL', 'CRWD', 'RARE', 'UMC', 'NTZ', 'SH', 'MRTX', 'JD', 'NIU', 'DAR', 'FSR', 'CCL', 'BLRX', 'SQ', 'ABBV', 'NCLH', 'LU', 'COST', 'TELL', 'ACHC', 'RCL', 'ROG', 'HTBX', 'VHC', 'FLIR', 'PYPL', 'COLM', 'ARKK', 'REAL', 'FSK', 'ROKU', 'ULTA', 'MHK', 'SSL', 'HTH', 'ALLK', 'LMND', 'RMD', 'IMO', 'NVST', 'BL', 'CUK', 'DVN', 'TAP', 'ELLO']

    status = {} # Whether we are buying or selling an 'active' stock.
    price_bought = {} # What price a stock was bought at.
    # highest_price = {} # Highest price.
    take_profit_counter = {} # Tracks your take profit count.
    amt_owned = {}

    tempHold = [] # list for temp. holding stocks that aren't performing optimally

    for stock in stocks:
        status[stock] = 'buy'
        price_bought[stock] = 0
        highest_price[stock] = 0
        take_profit_counter[stock] = 0

    # In case the program crashed, make sure that there are no open positions
    # or orders before starting to analyze. If there are, log the stock's
    # status as 'buy'.
    open_positions = api.list_positions()
    for position in open_positions:
        if position.symbol in stocks:
            status[position.symbol] = 'sell'
            price_bought[position.symbol] = position.avg_entry_price
            amt_owned[position.symbol] = abs(int(api.get_position(position.symbol).qty))
        else:
            continue
    open_orders = api.list_orders()
    for order in open_orders:
        if order.symbol in stocks:
            if status[order.symbol] == 'sell':
                if price_bought[order.symbol] != 0:
                    continue
                else:
                    price_bought[order.symbol] = order.filled_avg_price
            else:
                status[order.symbol] = 'sell'
                price_bought[order.symbol] = order.filled_avg_price
        else:
            stocks.append(order.symbol)
            status[order.symbol] = 'sell'

    # Stocks we are going to focus on trading
    trade_list = []
    # Main loop that analyzes, trades, and sleeps.
    while True:
        # Only trade and analyze if the market is open
        while market_status() == True:
            # Analyze for the top five stocks we'll trade.
            print("Finding the top five stocks to trade...")
            print()
            sma9_dict = {} # The difference between a stocks SMA9 now and yesterday.
            analysis_dict = {} # Holds the stock and their SMA50 and SMA200 difference to find the top ten performing stocks of the day.
            for stock in stocks:
                print(f"Analyzing {stock}...")
                # Get the data necessary for formulas. Periods 50 and 200.
                data = get_historical_data(stock, '1D', 200)
                print()
                # Make sure the data up-to-date feature doesn't throw a false.
                if data.empty == True:
                    break
                else:
                    data = data[stock]
                sma9 = ta.sma(data['close'], length=9)
                sma50 = ta.sma(data['close'], length=50).values[-1]
                sma200 = ta.sma(data['close'], length=200).values[-1]
                analysis_dict[stock] = sma50 / sma200 # Percentage difference rather than dollar
                sma9_dict[stock] = sma9.values[-1] - sma9.values[-2]
                
            analysis_dict = sorted(analysis_dict.items(), key=lambda x: x[1], reverse=True)
            analysis_list = []
            for i in analysis_dict:
                # Verifies positive movement and gets rid of stocks with NaN values.
                if (sma9_dict[i[0]] > 0) and (sma200 > 0) and (sma50 > 0):
                    if i[0] not in tempHold:
                        analysis_list.append(i[0])
            trade_list = analysis_list[:5]
                
            # Check the stocks we own against the stocks we want to own. Sell any stocks we don't want and reset the active stock dictionary.
            ownedStocks = []
            for ticker, position in status.items():
                if position == 'sell':
                    ownedStocks.append(ticker)
                else:
                    continue

                for stock in ownedStocks:
                    if stock in trade_list:
                        continue
                    else:
                        sell(stock, 1)
                        price_bought[stock] = 0
                        highest_price[stock] = 0
                        status[stock] = 'buy'
            print(f"The top five stocks are currently:")
            for i in range(len(trade_list)):
                print(f"{i + 1}. {trade_list[i]}")
            print()

            # If it is time to buy then analyze to buy.
            for stock in trade_list:
                if status[stock] == 'buy':
                    if stock in tempHold:
                        break
                    print(f"Analyzing {stock} for indicators to buy.")
                    print(f"Current Time: {datetime.datetime.now().time()}.")
                    # Get the data necessary for formulas. Periods 50 and 200.
                    data = get_historical_data(stock, '1D', 200)
                    # Make sure the data up-to-date feature doesn't throw a false.
                    if data.empty == True:
                        break
                    else:
                        data = data[stock]
                    # Run analysis test. If stock passes test, buy.
                    if sma(data, stock):
                        stocks_owned = 0
                        for i in list(status.values()):
                            if i == 'sell':
                                stocks_owned += 1
                        price_bought[stock] = buy(stock, stocks_owned)
                        highest_price[stock] = copy.copy(price_bought[stock])
                        status[stock] = 'sell'
                        amt_owned[stock] = abs(int(api.get_position(stock).qty))
                        print()
                    else:
                        print()
                        continue
                    
                elif status[stock] == 'sell':
                    print(f"Analyzing {stock} for indicators to sell.")
                    print(f"Current Time: {datetime.datetime.now()}.")
                    # Get the data necessary for formulas.
                    data = get_historical_data(stock, '1D', 200)
                    if data.empty == True:
                        print()
                        break
                    else:
                        data = data[stock]

                    current_price = currentPrice(data)
                    if current_price > highest_price[stock]:
                        highest_price[stock] = current_price

                    # Check stop loss: if loss of 2% total portfolio value for a single stock, sell all.
                    if stopLoss(highest_price[stock], current_price, price_bought[stock], amt_owned[stock]):
                        sell(stock, 1)
                        tempHold.append(stock)
                        price_bought[stock] = 0
                        highest_price[stock] = 0
                        amt_owned[stock] = 0
                        status[stock] = 'buy'
                        print()
                        break
                    # Check take profit, every 40% gain on a stock, sell 20% of shares owned.
                    
                    # elif takeProfit(take_profit_counter[stock], price_bought[stock], current_price): 
                    #     sell(stock, 0.20)
                    #     print()
                    #     continue

                    # If no indicators to sell, hold and continue analyzing other stocks.
                    else:
                        print()
                        continue


            # Take a break after checking each stock before looping again.
            print("Taking a break...")
            print()
            time.sleep(270)

        # If the market isn't open, sleep until the market is open.
        if market_status() == False:
            print("The market is no longer open.")
            print("Resetting variables...")
            print()
            tempHold = []
            print(f"Sleeping until the market re-opens.")
            print()
            time.sleep(time_to_open())



if __name__ == '__main__':
    print()
    run_bot()