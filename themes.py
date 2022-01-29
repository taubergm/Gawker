import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv ('gawker_hits.csv')

print(df)

def num_themes(df):
    plt.clf()

    df['date'] = pd.to_datetime(df['date'])
    df = df["main_theme"].value_counts()

    frame = {
            "theme": df.index,
            "num": df,
        }

    print(frame)

    theme_df = pd.DataFrame(frame)
    theme_df = theme_df.sort_values(by='num', ascending=True)
    theme_df['theme'] = theme_df['theme'].str.upper()
    
    

    fig, ax = plt.subplots(figsize=(14, 8))
    plt.rcParams.update({'font.size': 15})    
    
        
    ax.barh(theme_df["theme"], theme_df["num"], align='center')
    ax.legend()
    plt.xlabel("Num Hit Stories")
    plt.ylabel("Major Theme")
    plt.title("Gawker Hit Stories by Theme")
    plt.savefig("hits_themes.png")

num_themes(df)
