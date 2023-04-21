import requests
from bs4 import BeautifulSoup

url = "https://www.kdnuggets.com/"
res = requests.get(url)
htmlData = res.content
parsedData = BeautifulSoup(htmlData, "html.parser")
soup = BeautifulSoup("<h1>Welcome to KDnuggets</h1>", "html.parser")
# print(parsedData.prettify())
# print(type(soup.h1))
# print(type(soup.h1.string))
# print(parsedData.title.string)

# anchors = parsedData.find_all('a')
# for a in anchors:
#     print(a['href'])

tags = parsedData.find_all("li", class_="li-has-thumb")
for tag in tags:
    print(tag.txt)

data = parsedData.select()