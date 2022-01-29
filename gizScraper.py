import feedparser as fp
import json
import newspaper
from newspaper import Article
from time import mktime
from datetime import datetime
import csv
import sqlite3
import re
import requests
from bs4 import BeautifulSoup

#create news database
conn = sqlite3.connect('giz_v1_content.sqlite')
conn.text_factory = bytes
cur = conn.cursor()

# Make some fresh tables using executescript()

try:
    cur.executescript('''

    CREATE TABLE Headlines (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        date    TEXT, 
        authors TEXT,
        reads   TEXT,
        url     TEXT UNIQUE,
        headline TEXT UNIQUE,
        keywords TEXT,
        summary TEXT,
        wordcount TEXT,
        content TEXT
    );

    ''')
except:
    print("database already exists")


def contains_digits(d):
    _digits = re.compile('\d')
    return bool(_digits.search(d))

def parse_byline(search_str):
            """
            Takes a candidate line of html or text and
            extracts out the name(s) in list form:
            >>> parse_byline('<div>By: <strong>Lucas Ou-Yang</strong>,<strong>Alex Smith</strong></div>')
            ['Lucas Ou-Yang', 'Alex Smith']
            """
            # Remove HTML boilerplate
            search_str = re.sub('<[^<]+?>', '', search_str)

            # Remove original By statement
            search_str = re.sub('[bB][yY][\:\s]|[fF]rom[\:\s]', '', search_str)

            search_str = search_str.strip()

            # Chunk the line by non alphanumeric tokens (few name exceptions)
            # >>> re.split("[^\w\'\-\.]", "Tyler G. Jones, Lucas Ou, Dean O'Brian and Ronald")
            # ['Tyler', 'G.', 'Jones', '', 'Lucas', 'Ou', '', 'Dean', "O'Brian", 'and', 'Ronald']
            name_tokens = re.split("[^\w\'\-\.]", search_str)
            name_tokens = [s.strip() for s in name_tokens]

            _authors = []
            # List of first, last name tokens
            curname = []
            delimiters = ['and', ',', '']

            for token in name_tokens:
                if token in delimiters:
                    if len(curname) > 0:
                        _authors.append(' '.join(curname))
                        curname = []

                elif not contains_digits(token):
                    curname.append(token)

            # One last check at end
            valid_name = (len(curname) >= 2)
            if valid_name:
                _authors.append(' '.join(curname))

            return _authors





# Set the limit for number of articles to download
LIMIT = 200

data = {}
data['newspapers'] = {}

currentDT = datetime.now()
script_date = str(currentDT.year) + "_" + str(currentDT.month) + "_" + str(currentDT.day) 
print(script_date)

# Loads the JSON files with news sites
with open('gizmodo.json') as data_file:
    companies = json.load(data_file)

count = 1

csv_articles  = []
# Iterate through each news company
for company, value in companies.items():
        
    # It uses the python newspaper library to extract articles
        print("Building site for ", company)
        paper = newspaper.build(value['link'], memoize_articles=False)
        newsPaper = {
            "link": value['link'],
            "articles": []
        }
        noneTypeCount = 0
        for content in paper.articles:
            if count > LIMIT:
                break
            try:
                content.download()
                content.parse()
            except Exception as e:
                print(e)
                print("continuing...")
                continue
            
            if (
                (re.match(".*gizmodo.com", content.url) is None) and
                (re.match(".*io9.com", content.url) is None) and 
                (re.match(".*kotaku.com", content.url) is None) and
                (re.match(".*deadspin.com", content.url) is None) and
                (re.match(".*jalopnik.com", content.url) is None) and
                (re.match(".*lifehacker.com", content.url) is None) and
                (re.match(".*theroot.com", content.url) is None) and
                (re.match(".*theinventory.com", content.url) is None)
                ):
                continue

            print(content.url)


            # START Special code since newspaper3k fails to get date and author on this site
            # also we want to get reads
            try:
                page = requests.get(content.url)
            except:
                continue

            print(content.url)

            soup = BeautifulSoup(page.content, 'html.parser')
            
            date_data = soup.find_all(class_="uhd9ir-0 lkqtha")
            if not date_data:
                continue
            else:
                date = date_data[0]['datetime']

            author_data = soup.find_all(class_='sc-1ib37xr-4 kwEdzC')
            try:
                author = parse_byline(str(author_data))[0]
            except:
                author = ""
        
            title = soup.title.string

            reads = 0
            spans = soup.find_all('span')
            for span in spans:
                m = re.match("<span>(\d+.\d+)K</span>", str(span))
                if m is not None:
                    reads = m.group(1)
            # END SPECIAL INSERT CODE

            article = {}
            article['title'] = content.title
            article['text'] = content.text
            article['authors'] = author
            article['link'] = content.url
            if (date is None):
                now = datetime.now()
                article['date'] = now.strftime("%Y-%m-%d %H:%M:%S")
            else:
                article['date'] = date
            article['headline'] = content.title
            content.nlp()
            article['keywords'] = '-'.join(content.keywords)
            article['summary'] = content.summary
            article['wordcount'] = str(len(article['text'].split()))
            article['reads'] = str(reads)
             # put this in a db
            cur.execute('''INSERT OR REPLACE INTO Headlines
            (date, authors, url, headline, reads, wordcount, keywords, summary, content) 
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            ( article['date'], article['authors'], article['link'], article['headline'],
                article['reads'], article['wordcount'],
                article['keywords'], article['summary'], article['text'] ) )
            conn.commit()
            newsPaper['articles'].append(article)



            csv_article  = {}
            csv_article['headline'] = content.title
            csv_article['authors'] = author
            try:
                csv_article['date'] = date.isoformat()
            except:
                print("bad date")
                csv_article['date'] = date

            csv_article['link'] = content.url
            csv_article['wordcount'] = len(article['text'].split())
            csv_article['reads'] = reads
            csv_articles.append(csv_article)

            print(count, "articles downloaded from", company, " using newspaper, url: ", content.url)
            count = count + 1
            noneTypeCount = 0
            count = 1
            data['newspapers'][company] = newsPaper


OUTFILE = "giz_%s.csv" % script_date
with open(OUTFILE, 'w') as output_file:
    keys = ['headline', 'date', 'authors', 'reads', 'wordcount', 'link']
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    for row in csv_articles:
        try:
            dict_writer.writerow(row)
        except:
            print("couldn't write row data")
    





