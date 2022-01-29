import sqlite3
import pandas as pd
import numpy as np


def clean_views(df):
    df.views = (df.views.replace(r'[KM]+$', '', regex=True).astype(float) * \
            df.views.str.extract(r'[\d\.]+([KM]+)', expand=False)
            .fillna(1)
            .replace(['K','M'], [10**3, 10**6]).astype(int))


def create_title_txt_file():
    con = sqlite3.connect("gawker.sqlite")
    cur = con.cursor()
    df = pd.read_sql_query("SELECT date, authors, title, views from Headlines", con)
    np.savetxt(r'title.txt', df['title'], fmt='%s')
    
    clean_views(df)
    top = df[df['views'] > 100000]
    np.savetxt(r'top_titles.txt', top['title'], fmt='%s')
    df.to_csv('title_views.csv', encoding='utf-8')
    hits = df[df['views'] > 1000000]
    hits.to_csv('hits_views.csv', encoding='utf-8')


