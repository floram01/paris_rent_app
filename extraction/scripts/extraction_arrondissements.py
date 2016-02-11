import pandas as pd
from pandas import DataFrame, Series
from urllib2 import urlopen
from bs4 import BeautifulSoup
import requests
import re
import time
from datetime import datetime

url = "http://www.seloger.com/immobilier/locations/immo-paris-75/bien-appartement/?LISTING-LISTpg=2"
r = requests.get(url)
soup =  BeautifulSoup(r.text)

def iter_through(num_pages):
    iter_obj= range(1,num_pages+1)
    extraction=[]
    for num_page in iter_obj:
        url = "http://www.seloger.com/immobilier/locations/immo-paris-75/bien-appartement/?LISTING-LISTpg={0}".format(num_page)
        r = requests.get(url)
        soup =  BeautifulSoup(r.text)
        soup_of_interest = soup.find_all('article')
        new_extraction= extract_from_soup(soup_of_interest)
        extraction+=new_extraction
        time.sleep(5)
        print 'page {0} scrapped'.format(num_page)
    timestamp= datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
    file_output='/Users/Flo/projects/paris_rent/extraction/extractions/arrondisements/new/data_large_'+ timestamp + '.csv'
    data=DataFrame.from_dict(extraction)
    data.to_csv(file_output, encoding='utf8', index=False)    
    return DataFrame.from_dict(extraction)


def extract_from_one(annonce):
    new=dict()
    price_pat= re.compile('[0-9.]+')
    try:
        new['img']=annonce.find('img')['src']
    except:
        new['img']= None
    try:
        new['desc'] = annonce.find('h2').a['title']
    except:
        new['desc'] = None 
    try:
        price_pat=re.compile('^([0-9]*)(\xa0)*([0-9]+)')
        price_match=price_pat.search(annonce.find('div', 'price').a.contents[0])
        price_clean=price_match.group(1)+price_match.group(3)
        new['price']= price_clean
    except:
        new['price']=None
    try:
        new['full_desc']= annonce.find('p','description').contents[0].strip()
    except:
        new['full_desc']= None  
    try:
        contents=annonce.find('ul','property_list').find_all('li')
        size_pat=re.compile('([0-9]+)\s')
        for i,_ in enumerate(contents):
            elem=contents[i].contents[0]
            if 'p' in elem:
                new['rooms_num']=size_pat.search(elem).group(1)
            elif 'm' in elem:
                new['surface']=size_pat.search(elem).group(1)
    except:
        new['rooms_num']= None
        new['surface']= None
    try:
        arr_pat=re.compile(r'Paris ([0-9]+)')
        new['arr']=arr_pat.search(annonce.find('h2').a['title']).group(1)
    except:
        new['arr']=None
    return new

def extract_from_soup(soup):
    extractions=[]
    for annonce in soup:
        new= extract_from_one(annonce)
        extractions.append(new)
    return extractions       