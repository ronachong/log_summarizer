import datetime
import requests

r1 = requests.get('https://api.darksky.net/forecast/61982b282ad0e8410101fb450a15edfc/37.7749,-122.4194')

r2date = datetime.datetime(2016, 9, 24)
r2timestamp = (r2date - datetime.datetime(1970, 1, 1)).total_seconds()
r2 = requests.get('https://api.darksky.net/forecast/61982b282ad0e8410101fb450a15edfc/37.7749,-122.4194,' + str(r2timestamp)[:-2])

current_conditions = r1.json()["currently"]
print "current temp:", current_conditions["temperature"]
print "current summary:", current_conditions["summary"]

sept24_conditions = r2.json()["daily"]["data"][0]
print "temp 9/24:", (sept24_conditions["temperatureMin"] + sept24_conditions["temperatureMax"])/2
print "9/24 summary:", sept24_conditions["summary"]

week_conditions = r1.json()["daily"]["data"]
total_degs = 0
for day in week_conditions:
    total_degs += (day["temperatureMin"] + day["temperatureMax"])/2
print "average temp:", total_degs/8
