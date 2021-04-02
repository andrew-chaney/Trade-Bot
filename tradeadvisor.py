# Program to analyze when to buy an sell stocks along with a text message analysis apporximately every 30 minutes.

# Ultimate goal is a slow, but steady, stream of income. Target strategy is buying when the 50-day SMA is above the 200-day SMA for any given stock. 
# Stop loss is never over 20% for a given stock, and you should never lose more than 2% of your overall portfolio value due to the decline of a single stock.
# Take profit is set so that every 40% increase in value for a stock you sell 20% of your shares in that stock.

import time
import pandas as pd
import pandas_ta as ta
import numpy as np
import datetime
from math import ceil, floor
from config import *
import alpaca_trade_api as tradeapi
from SMS import *

BASE_URL = "https://paper-api.alpaca.markets"
api = tradeapi.REST(API_KEY, API_SECRET_KEY, BASE_URL)

number = 'ENTER PHONE NUMBER IN EMAIL FORM HERE'

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
############################### MAIN CODE ##############################
########################################################################

def run_bot():
    # Run the bot non-stop

    # A list of stocks to analyze
    stocks = ['TSLA', 'MSFT', 'SPY', 'AMD', 'AAPL', 'PLUG', 'NVDA', 'SPT', 'AMZN', 'PTON', 'ISRG', 'TWLO', 'PRPL', 'GRWG', 'VALE', 'WKHS', 'FB', 'DIS', 'NFLX', 'BABA', 'DKNG', 'SPCE', 'CXO', 'GME', 'ICLN', 'NKE', 'LMT', 'BLK', 'SNE', 'UBER', 'AEP', 'ERIC', 'MCHP', 'APTV', 'ETSY', 'KEYS', 'LH', 'TCOM', 'HUBS', 'GNRC', 'FSLY', 'APHA', 'LVGO', 'INSG', 'SE', 'APPS', 'BLNK', 'DOCU', 'CGC', 'TDOC', 'SNAP', 'GOOGL', 'NKLA', 'PLL', 'RTX', 'LI', 'NIO', 'KIRK', 'PRPLW', 'ZM', 'FVRR', 'TRIL', 'NLS', 'PRTS', 'QDEL', 'DQ', 'BTAI', 'AWH', 'SITM', 'ENPH', 'PEIX', 'ARCT', 'OSTK', 'CRDF', 'KSPN', 'IMVT', 'RUN', 'CELH', 'PRPH', 'EXPI', 'NGD', 'DPHCW', 'PACB', 'CMBM', 'SEDG', 'GLG', 'TWST', 'IMAB', 'REGI', 'OIIM', 'PINS', 'GSHD', 'ELLO', 'GRVY', 'JKS', 'BAND', 'FSM', 'NET', 'VAPO', 'BNTX', 'SAM', 'STKL', 'TRVN', 'DSKE', 'SWBI', 'AMRC', 'PNTG', 'FLGT', 'DRD', 'AHCO', 'BWMX', 'CARR', 'SAVA', 'SWTX', 'FTCH', 'CRNC', 'ACMR', 'GSX', 'FUTU', 'NOVA', 'TTD', 'NFE', 'ZS', 'CALX', 'PSNL', 'PDEX', 'KROS', 'FATE', 'DNLI', 'FIVN', 'OTRK', 'SUMR', 'AVXL', 'CRWD', 'RARE', 'UMC', 'NTZ', 'SH', 'MRTX', 'JD', 'RIDEW', 'NIU', 'DAR', 'RYCEY', 'FSR', 'DJI', 'IXIC', 'GSPC', 'CCL', 'DNKN', 'BLRX', 'SQ', 'ABBV', 'NCLH', 'LU', 'COST', 'TELL', 'ACHC', 'RUT', 'RCL', 'ROG', 'HTBX', 'VHC', 'FLIR', 'PYPL', 'COLM', 'ARKK', 'REAL', 'FSK', 'ROKU', 'ULTA', 'CHWRF', 'MHK', 'SSL', 'FSUMF', 'BGAOY', 'WPX', 'HTH', 'ALLK', 'LMND', 'RMD', 'IMO', 'PHJMF', 'NLLSF', 'NVST', 'BL', 'CUK', 'DVN', 'TAP']
    
    # Stocks we are going to focus on trading
    trade_list = []
    performer_list = []
    combo_list = [] # list of stocks that overlap from the trade list and the performance list
    # Main loop that analyzes, trades, and sleeps.
    while True:
        # Only trade and analyze if the market is open
        while market_status() == True:
            # Analyze for the top ten stocks we'll trade.
            print("Finding the top ten stocks to trade...")
            print()
            sma9_dict = {} # The difference between a stocks SMA9 now and yesterday.
            analysis_dict = {} # Holds the stock and their SMA50 and SMA200 difference to find the top ten performing stocks of the day.
            percentdiff_dict = {} # Percentage difference from current price to previous close
            for stock in stocks:
                print(f"Analyzing {stock}...")
                # Get the data necessary for formulas. Periods 50 and 200.
                data = get_historical_data(stock, '1D', 200)
                # Make sure the data up-to-date feature doesn't throw a false.
                if data.empty == True:
                    continue
                else:
                    data = data[stock]
                sma9 = ta.sma(data['close'], length=9)
                sma50 = ta.sma(data['close'], length=50).values[-1]
                sma200 = ta.sma(data['close'], length=200).values[-1]
                analysis_dict[stock] = sma50 / sma200 # Percentage difference rather than dollar
                try:
                    sma9_dict[stock] = sma9.values[-1] - sma9.values[-2]
                except Exception as e:
                    print("NaN Value...")
                    print(e)
                    print()
                    continue
                # Get the percentage gain/loss from yesterday's close to current price
                currentPrice = data['close'].values[-1]
                yesterdayClose = data['close'].values[-2]
                percentdiff = float(currentPrice) / float(yesterdayClose)
                percentdiff_dict[stock] = percentdiff
                print()

                
            analysis_dict = sorted(analysis_dict.items(), key=lambda x: x[1], reverse=True)
            percentdiff_dict = sorted(percentdiff_dict.items(), key=lambda x: x[1], reverse=True)
            analysis_list = [] # For probability analysis from analysis dict
            diff_list = [] # For current performers from percentdiff_dict
            for i in analysis_dict:
                # Verifies positive movement and gets rid of stocks with NaN values.
                try:
                    if (sma9_dict[i[0]] > 0) and (sma200 > 0) and (sma50 > 0):
                        analysis_list.append(i[0])
                except Exception:
                    continue
            trade_list = analysis_list[:10]
                
            for i in percentdiff_dict:
                diff_list.append(i[0])
            performer_list = diff_list[:10]

            print("Top Ten Stocks Consistently Performing Above Average:")
            projected_str = "\nTop Ten Stocks Consistently Performing Above Average:\n"
            for i in range(len(trade_list)):
                print(f"{i + 1}. {trade_list[i]}")
                projected_str += f"{i + 1}. {trade_list[i]}\n"
            print()

            # Organize stocks by the percent gain and loss from yesterday's close price to current price
            print("Top Ten Current Performing Stocks:")
            diff_str = "Top Ten Current Performing Stocks:\n"
            for i in range(len(performer_list)):
                print(f"{i + 1}. {performer_list[i]}")
                diff_str += f"{i + 1}. {performer_list[i]}\n"
            print()

            # Check for any overlaps
            for stock in performer_list:
                if stock in trade_list:
                    combo_list.append(stock)
            combo_list = combo_list[:10]
            print("Stocks Consistently Above Average and Currently Performing Well:")
            combo_str = "Stocks Consistently Above Average and Currently Performing Well:"
            for i in range(len(combo_list)):
                combo_str += "\n"
                print(f"{i + 1}. {combo_list[i]}")
                combo_str += f"{i + 1}. {combo_list[i]}"

            text("ANALYSIS", projected_str + diff_str + combo_str, number)
            
           

             # Take a break after checking each stock before looping again.
            print("Taking a break...")
            print()
            time.sleep(1745) # sleep for thirty minutes

        # If the market isn't open, sleep until the market is open.
        if market_status() == False:
            print("The market is no longer open.")
            print("Resetting variables...")
            print()
            print(f"Sleeping until the market re-opens.")
            print()
            time.sleep(time_to_open())



if __name__ == '__main__':
    print()
    run_bot()
