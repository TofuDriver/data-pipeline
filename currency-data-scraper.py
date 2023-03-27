import requests


currency_codes = ["AUD", "GBP", "BRL", "HUF", "HKD", "DKK", "EUR", "ILS", "INR", "IDR",
                  "CAD", "CNY", "MYR", "MXN", "NZD", "NOK", "PKR", "PLN", "RUB", "SGD",
                  "TWD", "THB", "TRY", "PHP", "CZK", "CLP", "SEK", "CHF", "ZAR", "KRW",
                  "UAH", "JPY"]
currency_codes_str = ",".join(currency_codes)

url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={currency_codes_str}&base=USD"
api_key = "zb7kksizkgvSrV7YLGfHLs8fpPUI94Pu"
headers = {
    "apikey": api_key
}

response = requests.request("GET", url, headers=headers)

with open("exchange_rates.csv", "wb") as file:
    file.write(response.content)
