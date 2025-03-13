import requests
from bs4 import BeautifulSoup

URL = "http://en.xcmg.com/en-ap/ext/ajax_prolist.jsp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "http://en.xcmg.com/en-ap/product/Road-Machinery/pro-list-1000121.htm",
    "Origin": "http://en.xcmg.com",
}

payload = {
    "flag": "1",
    "data1": "",
    "data2": "1000121",
    "data3": "",
    "data4": "",
    "data5": "",
    "data6": "",
    "nowPage": "1"
}

response = requests.post(URL, data=payload, headers=HEADERS)

if response.status_code == 200:
    print("Response content:\n", response.text[:1000])  # Print first 1000 characters
else:
    print(f"Failed to fetch data, Status Code: {response.status_code}")
