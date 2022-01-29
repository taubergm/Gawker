import requests
from bs4 import BeautifulSoup
import re
import csv
import sqlite3
import sys


#create news database
conn = sqlite3.connect('gawker.sqlite')
conn.text_factory = bytes
cur = conn.cursor()

# Make some fresh tables using executescript()

try:
    cur.executescript('''

    CREATE TABLE Headlines (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        date    TEXT, 
        author TEXT,
        url     TEXT UNIQUE,
        title   TEXT,
        image   TEXT,
        reads TEXT
    );

    ''')
except:
    print("database already exists")


urls = set()   # set of stories from gawker

OUTFILE = "gawker_all.csv"

with open(OUTFILE, 'w') as output_file:
    
    keys = ['date', 'author', 'url', 'title', 'image', 'reads', 'content']
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    
    for i in range(1, 3):

        page = requests.get("http://www.gawker.com/page_%s" % i)
        #print(page)

        #print page.content
        
        soup = BeautifulSoup(page.content, 'html.parser')
        #print(soup.prettify())

        
        for link in soup.find_all('a', href=True):
            url = link['href']
            if not re.match(".*http", url):
                if not re.match(".*page_", url):
                    if (url != "/"):
                        urls.add(url)
                #print url




for url in urls:

    url = "https://gawker.com" + url
    print url


    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    print page.content
    #print soup.prettify()
    views = soup.find(class_='meta__views')
    views = re.match(".*>(.*)<", str(views)).group(1)
    print views
    
    #title = soup.find('title')
    #print title

    meta = soup.find_all(class_="meta__text")
    for line in meta[0]:
        m = re.match(".*datetime=\"(.*)T(.*)\"", str(line))
        if m is not None:
            date = m.group(1)
            time = m.group(2)

    



    print date
    print time


    title = soup.find("meta",  property="og:title")['content']
    print title

    author = soup.find(class_="meta__byline")
    author = re.match(".*>(.*)<", str(author)).group(1)
    print author

    page_type = soup.find("meta",  property="og:type")['content']
    print page_type


    # steal get_content from newsScrapre
    content = soup.findAll(class_="align--bleed")
    print content

    #div = soup.findAll("div", {"class": "post-content"})
    #print div
    





    sys.exit()




        


