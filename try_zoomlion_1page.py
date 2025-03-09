import requests
from bs4 import BeautifulSoup

url = "https://en-product.zoomlion.com/ext/ajax_proList.jsp"
payload = {
    "flag": "pro",
    "sCat": "57",
    "tCat": "",
    "htzParam": "[]",
    "key": "",
    "chanelld": "22482",
    "nowPage": "1",
    "page_size": "6"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://en-product.zoomlion.com/product/pro_list.htm?sCat=57",
    "Origin": "https://en-product.zoomlion.com",
}

response = requests.post(url, data=payload, headers=headers)
html_content = response.text

# Parse HTML response
soup = BeautifulSoup(html_content, "html.parser")

# Extract product details
products = []
for item in soup.find_all("li"):
    name = item.find("div", class_="tit tit22")
    category = item.find("div", class_="con con16")
    specs = item.find_all("div", class_="line line01 con16")

    # Extract individual specifications
    weight = power = capacity = None
    for spec in specs:
        if "Operating weight" in spec.text:
            weight = spec.find("span", class_="num num01").text.strip()
        elif "Rated power" in spec.text:
            power = spec.find("span", class_="num num01").text.strip()
        elif "Standard capacity" in spec.text:
            capacity = spec.find("span", class_="num num01").text.strip()

    if name and category:
        products.append({
            "name": name.text.strip(),
            "category": category.text.strip(),
            "operating_weight": weight,
            "rated_power": power,
            "standard_capacity": capacity,
        })

# Print extracted data
for p in products:
    print(p)
