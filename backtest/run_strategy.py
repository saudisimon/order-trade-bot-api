import backtrader as bt
import pandas as pd
import pybit, os, config, time
from datetime import datetime
from strategies.mean_reversion_strategy import MeanReversionStrategy

# Define your Bybit API credentials
# Define your Bybit API credentials
API_KEY = os.environ.get('API_KEY_TESTING', config.API_KEY_TESTING)
API_SECRET = os.environ.get('API_SECRET_TESTING', config.API_SECRET_TESTING)

# Define the symbol and timeframe for the data feed
symbol = 'ETHUSDT'  # Replace with the desired trading pair
timeframe = '15'  # Replace with the desired timeframe

# Define the BybitDataFeed class that extends bt.feeds.GenericCSVData
class BybitDataFeed(bt.feeds.GenericCSVData):
    params = (
        ('nullvalue', float('nan')),
        ('dtformat', '%Y-%m-%d %H:%M:%S'),
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', -1),
        ('openinterest', -1),
    )

# Create a PyBit client instance
# client = pybit.HTTP(endpoint='https://api-testnet.bybit.com', api_key=API_KEY, api_secret=API_SECRET)

# num_bars = 365
# Fetch historical data from the Bybit API
# klines = client.query_kline(
#     symbol=symbol,
#     interval=timeframe,
#     limit=num_bars,
# )
batch_size = 200
start_time = int(time.time()) - batch_size * 86400

# client = bybit.bybit(test=True, api_key=API_KEY, api_secret=API_SECRET)
# response = client.LinearKline.LinearKline_get(symbol="DOTUSDT", interval="5", **{'from':start_time}).result()
# response = client.Kline.Kline_get(
#     symbol=symbol,
#     interval=timeframe,
#     **{'from':start_time},  # Replace with the desired start time in Unix timestamp format
# ).result()
# klines = response[0]['result']
# print(klines)

client = pybit.HTTP(endpoint='https://api-testnet.bybit.com', api_key=API_KEY, api_secret=API_SECRET)
# Fetch the K-line data from the Bybit API
params = {
    'symbol': symbol,
    'interval': timeframe,
    'from': start_time
}
response = client.query_kline(**params)
print(response)
klines = response['result']
# klines = client.kline.get_kline(
#     symbol=symbol,
#     interval=timeframe,
#     from_time=start_time
# )

# Convert the fetched data to the required format for the data feed
data = []
for kline in klines:
    data.append([
        datetime.fromtimestamp(kline['open_time']).strftime('%Y-%m-%d %H:%M:%S'),
        kline['open'],
        kline['high'],
        kline['low'],
        kline['close'],
        kline['volume'],
        datetime.fromtimestamp(kline['id']).strftime('%Y-%m-%d %H:%M:%S'),
        -1,  # Set open interest to 0 or -1 if not available
    ])

# Convert the K-line data to a Pandas DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
csv_file_path = '../kline_data.csv'  # Replace with your desired file path
df.to_csv(csv_file_path, index=False)

# Create a data feed from the fetched K-line data
# data = bt.feeds.GenericCSVData(
#     dataname=csv_file_path,
#     dtformat=1,  # Date format (0: 'yyyy-mm-dd', 1: 'yyyymmdd', 2: 'dd-mm-yyyy')
#     datetime=0,  # Column index or column name containing datetime
#     open=1,  # Column index or column name containing opening price
#     high=2,  # Column index or column name containing high price
#     low=3,  # Column index or column name containing low price
#     close=4,  # Column index or column name containing closing price
#     volume=5,  # Column index or column name containing volume
#     openinterest=-1,  # Column index or column name containing open interest (-1 if not available)
#     timeframe=bt.TimeFrame.Days,  # Specify the timeframe (e.g., bt.TimeFrame.Days, bt.TimeFrame.Minutes, etc.)
# )

# Create a data feed using the BybitDataFeed class
data_feed = BybitDataFeed(dataname=csv_file_path)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # Add the data feed to cerebro
    cerebro.adddata(data_feed)

    cerebro.addstrategy(MeanReversionStrategy)



    cerebro.run()
    cerebro.plot(volume=False)
