import csv
import traceback
import random
import pandas as pd
import os
import configparser
import time
from tqdm import tqdm
import json
import requests
from lxml.html import fromstring
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

config = configparser.ConfigParser()
config.sections()
config.read('pages.txt')

def getGUID(string):
    return string.rsplit('/', 2)[-2]

def splitingfromstring(string):
    TotalString = str(string.rsplit('/', 2)[1])
    return TotalString

def getScrapedIDs(source):
    if source == 'issuu':
        scraped_ids = pd.read_csv('issuu.csv', header = None)        
    elif source == 'calameo':
        scraped_ids = pd.read_csv('calameo.csv', header = None)
    return([x[0] for x in scraped_ids.values])

def updateScrapedIDs(source, ID):
    if source == 'issuu':
        with open('issuu.csv','a') as f:
            f.write('\n' + ID)
    elif source == 'calameo':
        with open('calameo.csv','a') as f:
            f.write('\n' + ID)

def errorLog(er):
    with open('error_log.txt','a') as f:
        f.write('\n' + er)

def calameo_headers():
    return {'Host': 'd.calameo.com',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'no-cors',
            'Referer': 'https://en.calameo.com/accounts/2556309',
            'Accept-Encoding': 'gzip,deflate,br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cookie': 'lang=en'
    }

def GetMethod(s, URL, headers=False, stream=False):
    if headers:
        r = s.get(url=URL, timeout=50, verify=False, allow_redirects=True,
                  headers=headers, proxies={"http": str(get_proxies())})
    else:
        r = s.get(url=URL, timeout=50, verify=False, allow_redirects=True, proxies={
            "http": str(get_proxies())})
    if r.status_code == 200:
        return r
    else:
        return None

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url, verify=False, timeout=50)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')][0])
            proxies.add(proxy)
    return proxies    
    
#######################
#######################
#######################


issuu_papers = str(config.get('issuu', 'Magazine')).split(',')
#random.shuffle(issuu_papers)
#for z in issuu_papers:
#    print(z)
#    scrape_issuu(z)

# calameo_papers = str(config.get('calameo', 'Magazine')).split(',')
# calameo_papers = [s.strip() for s in calameo_papers]
# for z in calameo_papers:
#     scrape_calameo(z)
    


z=issuu_papers[0]

s = requests.session()
z = str(z).strip()
print('Scraping '+'https://issuu.com/'+z+'/docs')
if not os.path.isdir('issuu/' + z):
    os.makedirs('issuu/' + z)
profile_title = splitingfromstring(
    'https://issuu.com/'+z+'/docs')
response = s.get('https://issuu.com/' +z+'/docs', verify=False)
url = response.url
# response = s.get('https://issuu.com/call/social-backend/v1/articles/maspormasimpreso/29-octubre-issuu?sortBy=pagenumbers', verify = False)
response = s.get('https://issuu.com/call/profile/v1/documents/' +
                 profile_title+'?offset=0&limit=100', verify=False)
data = response.json()
total = data['total']
step = 501
CollectedArticles = getScrapedIDs('issuu')
for i in range(0, total, step):
    response = s.get(
        'https://issuu.com/call/profile/v1/documents/' + profile_title + '?offset=' + str(
            i) + '&limit=500',
        verify=False)
    data = response.json()
    AllDatas = data['items']
    for doc in AllDatas:
        uri = str(doc['uri'])
        s.get(url+'/'+uri, verify=False)
        print('here')
        print(profile_title)
        print(uri)
        print('https://reader3.isu.pub/'+profile_title+'/'+uri+'/reader3_4.json')
        singlepaper = s.get(
            'https://reader3.isu.pub/'+profile_title+'/'+uri+'/reader3_4.json', verify=False)
        singlepaper_data = singlepaper.json()
        PublishDate = singlepaper_data['document'].get(
            'originalPublishDate')
        AllPages = singlepaper_data['document']['pages']
        if str(doc['documentId']).lower().strip() not in CollectedArticles:
            edition_dir = 'issuu/' + z + '/' + PublishDate.replace('-', '_')
            if not os.path.isdir(edition_dir):
                os.makedirs(edition_dir)
            meta = doc['title'], doc['documentId'], doc['publishDate'], len(AllPages)
            pd.DataFrame([meta]).to_csv(edition_dir + '/meta.csv',
                                        header = None,
                                        quoting = csv.QUOTE_ALL)
            page_count = 0
            for singleimage in AllPages:
                page_count += 1
                downloadurl = singleimage['imageUri']
                imageresponse = s.get(
                    'http://'+downloadurl, verify=False)
                with open(edition_dir + "/" + str(page_count) + '.jpg', 'wb') as f:
                    f.write(imageresponse.content)
                if (page_count == len(AllPages)):
                    allClear = True
                    updateScrapedIDs('ISSUU', str(doc['documentId']).lower().strip())
            if page_count == len(AllPages):
                updateScrapedIDs('issuu', str(doc['documentId']).lower().strip())
