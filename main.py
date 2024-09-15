from fastapi import FastAPI , Query
from fastapi.middleware.cors import CORSMiddleware
import os
import json as j 
from bs4 import BeautifulSoup as bs
import requests as rq
import datetime as dt
from urllib.request import urlopen

app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],  allow_methods=["*"],allow_headers=["*"],
)

loc = os.path.dirname(__file__)
os.chdir(loc)

# تحميل ملف JSON
def load_json_file():
    while True:
        try:
            with open(f"/var/task/database.json", "r") as thefile:
                return j.load(thefile)
        except (j.decoder.JSONDecodeError, FileNotFoundError):
            initial_data = {
                "times":[]
            }
            with open(f"/var/task/database.json", "w") as controler:
                j.dump(initial_data, controler, indent=4)

# حفظ ملف JSON
def save_json_file(data):
    with open(f"/var/task/database.json", "w") as f:
        j.dump(data, f, indent=4)

# تحميل أوقات الصلاة
def fetch_prayer_times(city, year, month):
    url = f'https://timesprayer.com/en/list-prayer-in-{city}-{year}-{month}.html'
    response = rq.get(url)
    soup = bs(response.content, "html.parser")
    times_table = soup.find(class_="prayertimerange").find_all('td')
    return times_table

# معالجة أوقات الصلاة
def process_prayer_times(times_table):
    the_database_list = [td.text for td in times_table]
    the_date_list = the_database_list[::7]
    the_times_list = [the_database_list[i].split()[0] for i in range(len(the_database_list)) if i % 7 != 0]
    the_times_during_list = [the_database_list[i].split()[1] for i in range(len(the_database_list)) if i % 7 != 0]
    return the_date_list, the_times_list, the_times_during_list

# تحديث ملف JSON بأوقات الصلاة
def update_json_with_prayer_times(json_data, date_list, times_list, times_during_list):
    for i in range(len(date_list)):
        daily_times = {
            "date_for": date_list[i],
            "all_times": times_list[i*6:(i+1)*6],
            "all_times_during": times_during_list[i*6:(i+1)*6],
        }
        json_data["times"].append(daily_times)
    save_json_file(json_data)

@app.get("/pray_times")
async def main():
    return {"msg":"Welcome to slatuna API if there is an error tell me on github 'https://github.com/AhmedFox2/Slatuna_API'"}

@app.get("/pray_times")
async def main():
    try:
        json_data = load_json_file()
        response = urlopen('http://ipinfo.io/json')
        data = j.load(response)
        city = data["city"]
        
        current_date = dt.datetime.now().date()
        current_year, current_month, current_day = current_date.year, current_date.month, current_date.day

        for month in range(current_month, 13):
            times_table = fetch_prayer_times(city, current_year, month)
            date_list, times_list, times_during_list = process_prayer_times(times_table)
            update_json_with_prayer_times(json_data, date_list, times_list, times_during_list)
        return json_data
    except Exception as e:
        return {"msg":f"{e}"}
