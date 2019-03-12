import requests
import time
from datetime import datetime

BITCOIN_API_URL = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/'
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/<YOUR-KEY-HERE>'
BITCOIN_PRICE_THRESHOLD_LOW = 3500
BITCOIN_PRICE_THRESHOLD_HIGH = 4350

def get_latest_bitcoin_price():
	response = requests.get(BITCOIN_API_URL)
	response_json = response.json()
	return float(response_json[0]['price_usd'])

def post_ifttt_webhook(event,value):
	#payload that will be sent to IFTTT service
	data = {'value1' : value}
	#inserts our desired event
	ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
	#sends a HTTP POST request to the webhook url
	requests.post(ifttt_event_url, json=data)
	
def format_bitcoin_history(bitcoin_history):
	rows = []
	for bitcoin_price in bitcoin_history:
		#format the date into a string: 'mm.dd.yyyy hh:mm'
		date = bitcoin_price['date'].strftime('%m.%d.%Y %H:%M')
		price = bitcoin_price['price']
		
		row = '{}: $<b>{}</b>'.format(date, price)
		rows.append(row)
	
	return '<br>'.join(rows)
	
def main():
	bitcoin_history = []
	once_per_24hr_flag = False
	counter = 0
	while True:
		price = get_latest_bitcoin_price()
		date = datetime.now()
		bitcoin_history.append({'date': date, 'price': price})
		
		#send an emergency notification
		if price < BITCOIN_PRICE_THRESHOLD_LOW or price > BITCOIN_PRICE_THRESHOLD_HIGH:
			if once_per_24hr_flag == False:
				post_ifttt_webhook('bitcoin_price_emergency', price)
				once_per_24hr_flag = True
		
		#send a telegram notification
		#once we have 5 items in our bitcoin_history send an update
		if len(bitcoin_history) == 5:
			post_ifttt_webhook('bitcoin_price_update', format_bitcoin_history(bitcoin_history))
			bitcoin_history = []
		
		#sleep for 5 minutes
		time.sleep(5 * 60)
		counter = counter + 1
		#reset flag once a day
		if counter == 288:
			once_per_24hr_flag = False
			counter = 1
	
if __name__ == '__main__':
	main()