import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import seaborn as sns



def clean_views(df):
    df.views = (df.views.replace(r'[KM]+$', '', regex=True).astype(float) * \
            df.views.str.extract(r'[\d\.]+([KM]+)', expand=False)
            .fillna(1)
            .replace(['K','M'], [10**3, 10**6]).astype(int))

def clean_authors(df):
    df.authors = df.authors.replace(r':.*', '', regex=True)
    df.authors = df.authors.replace(r'And .*', '', regex=True)
    
def millions(x, pos):
    'The two args are the value and tick position'
    return '%1.1fM' % (x * 1e-6)

def thousands(x, pos):
    'The two args are the value and tick position'
    return '%1.1fK' % (x * 1e-3)

def plot_bar(df, xcol, ycol, color, title, filename):
    plt.bar(
    df[xcol],
    df[ycol],
    color=color
    )
    plt.title(title)
    plt.xticks(rotation=90)
    plt.savefig(filename)


def power_law(df):
    plt.clf()
    plt.rcParams.update({'font.size': 11})    
    plt.xlabel("Story Views")
    plt.ylabel("Num Stories")
    plt.title("Histogram of Story Views (bottom of distribution)")

    top = df[df['views'] >= 100000]
    rest = df[df['views'] < 100000]
    num_bins = 1000
    plt.ylim(top=5000) 
    plt.xlim(xmax=100000)     
    n, bins, patches = plt.hist(rest['views'], num_bins, facecolor='blue', alpha=0.5)
    plt.savefig("botton_views_histogram")



def gini(x, w=None):
    # The rest of the code requires numpy arrays.
    x = np.asarray(x)
    if w is not None:
        w = np.asarray(w)
        sorted_indices = np.argsort(x)
        sorted_x = x[sorted_indices]
        sorted_w = w[sorted_indices]
        # Force float dtype to avoid overflows
        cumw = np.cumsum(sorted_w, dtype=float)
        cumxw = np.cumsum(sorted_x * sorted_w, dtype=float)
        return (np.sum(cumxw[1:] * cumw[:-1] - cumxw[:-1] * cumw[1:]) / 
                (cumxw[-1] * cumw[-1]))
    else:
        sorted_x = np.sort(x)
        n = len(x)
        cumx = np.cumsum(sorted_x, dtype=float)
        # The above formula, with all weights equal to 1 simplifies to:
        return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n



#########
## PAGREVIEWS OVER TIME
#########

def page_views_over_time(df, name):
    plt.clf()
    date_views = df.groupby(df["date"])["views"].sum()
    frame = {
            "ds": date_views.index,
            "views": date_views,
        }
    views_df = pd.DataFrame(frame)
    views_df.ds = pd.to_datetime(views_df.ds)
    views_df.set_index("ds", inplace=True)

    views_month_df = views_df.groupby([lambda x: x.year, lambda x: x.month]).sum()
    frame = {
            "month": views_month_df.index,
            "views": views_month_df['views'],
        }

    views_month_df = pd.DataFrame(frame)
    views_month_df['ds'] = views_month_df['month'].apply(lambda x: '_'.join(str(v) for v in x))
    views_month_df['ds'] = pd.to_datetime(views_month_df['ds'], format="%Y_%m")
    views_month_df.set_index("ds", inplace=True)


    fig, ax = plt.subplots(figsize=(17, 10))
    ax.xaxis_date()

    print(views_month_df)
    
    #views_month_df.plot(ax=ax)
    plt.plot(views_month_df.index, views_month_df['views'])
    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    formatter = FuncFormatter(millions) 
    ax.yaxis.set_major_formatter(formatter)
    plt.title("Total Gawker Pageviews per Month")
    plt.savefig("{}_total_views.png".format(name))


#########
## NUM STORIES OVER TIME
#########

def num_stories_over_time(df, name):
    plt.clf()
    date_stories = df[
            [
                "date",
                "title"
            ]
        ]

    date_stories['date'] = pd.to_datetime(date_stories['date'])
    date_stories = df["date"].value_counts()

    frame = {
            "ds": date_stories.index,
            "stories": date_stories,
        }

    stories_df = pd.DataFrame(frame)
    stories_df.ds = pd.to_datetime(stories_df.ds)
    stories_df.set_index("ds", inplace=True)

    stories_month_df = stories_df.groupby([lambda x: x.year, lambda x: x.month]).sum()
    frame = {
            "month": stories_month_df.index,
            "stories": stories_month_df['stories'],
        }

    stories_month_df = pd.DataFrame(frame)
    stories_month_df['ds'] = stories_month_df['month'].apply(lambda x: '_'.join(str(v) for v in x))
    stories_month_df['ds'] = pd.to_datetime(stories_month_df['ds'], format="%Y_%m")
    stories_month_df.set_index("ds", inplace=True)

    print(stories_month_df)
    fig, ax = plt.subplots(figsize=(17, 10))
    ax.xaxis_date()
    plt.plot(stories_month_df.index, stories_month_df['stories'])
    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.title("{} - Total Stories per Month".format(name))
    #plt.show()
    plt.savefig("{}_stories_month.png".format(name))
    


def story_length_over_time(df, name):
    plt.clf()
    
    #df['30day_rolling_avg'] = df['length'].rolling(30).mean()
    #print(df['30day_rolling_avg'])
    #df_ten = df.iloc[::30, :]
    
    date_lengths = df.groupby(df["date"])["length"].mean()
    frame = {
            "ds": date_lengths.index,
            "length": date_lengths,
        }
    length_df = pd.DataFrame(frame)
    length_df.ds = pd.to_datetime(length_df.ds)
    length_df.set_index("ds", inplace=True)

    length_month_df = length_df.groupby([lambda x: x.year, lambda x: x.month]).mean()
    frame = {
            "month": length_month_df.index,
            "length": length_month_df['length'],
        }

    length_month_df = pd.DataFrame(frame)
    length_month_df['ds'] = length_month_df['month'].apply(lambda x: '_'.join(str(v) for v in x))
    length_month_df['ds'] = pd.to_datetime(length_month_df['ds'], format="%Y_%m")
    length_month_df.set_index("ds", inplace=True)



    fig, ax = plt.subplots(figsize=(15, 10))    
    plt.plot(length_month_df.index, length_month_df['length'])
    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.title("{} - Avg Story Length per Month".format(name))
    plt.gcf().autofmt_xdate()
    ax.xaxis_date()    
    ax.xaxis.set_major_locator(mdates.YearLocator())    
    plt.savefig("{}_story_length_month.png".format(name))



############
# BEST TIME OF DAY TO PUBLISH
##########
def story_length(df, name):
    plt.clf()
    df['hour'] = df['time'].str.slice(0, 2)
    df["hour"] = pd.to_numeric(df["hour"])

    bins = np.linspace(0, 1000, 50)

    fig, ax = plt.subplots(figsize=(15, 10))
    plt.hist(
        df["length"],
        bins,
        color=["SkyBlue"],
    )
    plt.title("Histogram of Gawker Story Length (in num words)")
    plt.xlabel('Num Words Per Story')
    plt.ylabel('Count')    
    plt.legend(loc="upper right")
    plt.savefig("{}_story_length.png".format(name))
    

def time_of_day(df, name):
    plt.clf()

    bins = np.linspace(0, 24, 24)

    plt.hist(
        df["hour"],
        bins,
    )
    plt.legend(loc="upper right")
    #plt.show()


    hour_views = df.groupby(df["hour"])["views"].sum().sort_values()
    frame = {
        "hour": hour_views.index,
        "total_views": hour_views,
    } 
    hour_views_df = pd.DataFrame(frame)
    #plot_bar(
    #        df=hour_views_df, 
    #        xcol="hour", 
    #        ycol="total_views", 
    #        color="SkyBlue",
    #        title="Number of Story Views by Hour published", 
    #        filename="hour_stories.png"
    #        )
    
    plt.clf()
    plt.rcParams.update({'font.size': 13})    
    fig, ax = plt.subplots(figsize=(17, 10))
    formatter = FuncFormatter(millions)    
    ax.bar(hour_views_df["hour"], hour_views_df["total_views"], align='center', color="SkyBlue")
    ax.legend()
    plt.ylabel("Total Views")
    plt.xlabel("Hour")
    plt.title("{} - Number of Story Views by Hour published".format(name))

    formatter = FuncFormatter(millions) 
    ax.yaxis.set_major_formatter(formatter)
    plt.savefig("{}_time_of_day.png".format(name))


############
# BEST DAY OF WEEK TO PUBLISH
##########

def day_of_week(df, name):
    plt.clf()

    df['my_dates'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['my_dates'].dt.day_name()
    
    #df['day_of_week'].value_counts().plot.bar() # num articles not views
    day_views = df.groupby(df["day_of_week"])["views"].sum()
    frame = {
        "day": day_views.index,
        "total_views": day_views,
    } 
    day_views_df = pd.DataFrame(frame)

    df_mapping = pd.DataFrame({
    'day': ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
    })
    
    sort_mapping = df_mapping.reset_index().set_index('day')
    day_views_df['day_num'] = day_views_df['day'].map(sort_mapping['index'])
    day_views_df = day_views_df.sort_values('day_num')
    
    
    plt.rcParams.update({'font.size': 13})    
    fig, ax = plt.subplots(figsize=(17, 10))
    
    formatter = FuncFormatter(millions)    
    ax.bar(day_views_df["day"], day_views_df["total_views"], align='center', color="SkyBlue")
    ax.legend()
    plt.ylabel("Total Views")
    plt.xlabel("Day")
    plt.title("{} Stories - Number of Views by Day of Week".format(name))
    ax.yaxis.set_major_formatter(formatter)

    
    plt.savefig("{}_day_of_week.png".format(name))
    



############
### TOP AUTHORS #######
############

def top_writers(df):

    # most stories by author
    author_stories = df['authors'].value_counts()
    frame = {
        "author": author_stories.index,
        "total_stories": author_stories,
    } 
    author_stories_df = pd.DataFrame(frame).sort_values(by='total_stories', ascending=False)
    author_stories_df = author_stories_df[author_stories_df['author'] != '']
    author_stories_df = author_stories_df.head(20)
    author_stories_df = author_stories_df[::-1]
    
    
    plt.clf()
    plt.rcParams.update({'font.size': 13})
    fig, ax = plt.subplots(figsize=(17, 13))
    formatter = FuncFormatter(thousands)
    ax.barh(author_stories_df["author"], author_stories_df["total_stories"], align='center', color="SkyBlue")
    ax.legend()
    plt.xlabel("Total Stories")
    plt.ylabel("Author")
    plt.title("Total Number of Stories by Author")
    ax.xaxis.set_major_formatter(formatter)
    
    plt.savefig("author_stories.png") 

    

    # most views by author
    author_views = df.groupby(df["authors"])["views"].sum()
    frame = {
        "author": author_views.index,
        "total_views": author_views,
    } 
    author_views_df = pd.DataFrame(frame).sort_values(by='total_views', ascending=False)
    author_views_df = author_views_df[author_views_df['author'] != '']
    author_views_df = author_views_df.head(20) 
    author_views_df = author_views_df[::-1]


    plt.clf()
    plt.rcParams.update({'font.size': 13})    
    fig, ax = plt.subplots(figsize=(17, 13))
    formatter = FuncFormatter(millions)
    ax.barh(author_views_df["author"], author_views_df["total_views"], align='center', color="SkyBlue")
    ax.legend()
    plt.xlabel("Total Views")
    plt.ylabel("Author")
    plt.title("Total Number of Views by Author")
    ax.xaxis.set_major_formatter(formatter)
    
    plt.savefig("author_views.png") 



#######3
### MAIN ####
########
con = sqlite3.connect("gawker.sqlite")
cur = con.cursor()
df = pd.read_sql_query("SELECT * from Headlines", con)

clean_views(df)
clean_authors(df)

df['year'] = pd.DatetimeIndex(df['date']).year
df = df[df['year'] >= 2000] # remove one bad date row
df = df[df['title'] != 'Front views'] # remove - not a real story
df['length'] = df['content'].str.split().str.len() # num words per story

hits = df[df['views'] >= 1000000]




############
### TOTALS #######
############

views = df['views'].sum()
print("TOTAL VIEWS = {} \n".format(views))

stories = len(df.index)
print("TOTAL STORIES = {} \n".format(stories))

#gini_coeff = gini(df['views'])
#print("gini = {}".format(gini_coeff))


avg_len_all = df['length'].median()
print("AVG STORY LEN = {} \n".format(avg_len_all))

avg_len_hits = hits['length'].median()
print("AVG HIT STORY LEN = {} \n".format(avg_len_hits))





power_law(df)
top_writers(df)
story_length(df, "all")
story_length(hits, "hits")
#story_length_over_time(df, "all")
#page_views_over_time(df, "all")
#num_stories_over_time(df, "all")
time_of_day(df, "all")
time_of_day(hits, "hits")

day_of_week(df, "All")
day_of_week(hits, "Hit")

page_views_over_time(df, "all")
num_stories_over_time(df, "all")
story_length_over_time(df, "All")



#Neetzan - most popular
Neetzan = df[df['authors'] == 'Neetzan Zimmerman']
# power law of views
Nolan = df[df['authors'] == 'Hamilton Nolan']


num_stories_over_time(Nolan, "Hamilton Nolan")
page_views_over_time(Neetzan, "Neetzan Zimmerman")
story_length_over_time(Nolan, "Hamilton Nolan")
num_stories_over_time(Neetzan, "Neetzan Zimmerman")


con.close()


