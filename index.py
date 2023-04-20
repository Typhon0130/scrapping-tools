import requests
from bs4 import BeautifulSoup

url = "https://www.kdnuggets.com"
res = requests.get(url)
htmlData = res.content
parsedData = BeautifulSoup(htmlData, "html.parser")
print(parsedData.prettify())