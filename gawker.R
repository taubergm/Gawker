if (!require(ggplot2)) {
  install.packages("ggplot2", repos="http://cran.us.r-project.org")
}
library(ggplot2)
if (!require(plyr)) {
  install.packages("plyr", repos="http://cran.us.r-project.org")
}
library(plyr)
if (!require(data.table)) {
  install.packages("data.table", repos="http://cran.us.r-project.org")
}
library(data.table)
if (!require(waffle)) {
  install.packages("waffle", repos="http://cran.us.r-project.org")
}
library(waffle)
if (!require(ggthemes)) {
  install.packages("ggthemes", repos="http://cran.us.r-project.org")
}
library(ggthemes)
if (!require(RSQLite)) {
  install.packages("RSQLite", repos="http://cran.us.r-project.org")
}
library(RSQLite)
if (!require(DBI)) {
  install.packages("DBI", repos="http://cran.us.r-project.org")
}
library(DBI)
if (!require(wordcloud)) {
  install.packages("wordcloud", repos="http://cran.us.r-project.org")
}
library(wordcloud)
if (!require(tm)) {
  install.packages("tm", repos="http://cran.us.r-project.org")
}
library(tm)
if (!require(SnowballC)) {
  install.packages("SnowballC", repos="http://cran.us.r-project.org")
}
library(SnowballC)
if (!require(stringr)) {
  install.packages("stringr", repos="http://cran.us.r-project.org")
}
library(stringr)
if (!require(tidytext)) {
  install.packages("tidytext", repos="http://cran.us.r-project.org")
}
library(textclean)
if (!require(textclean)) {
  install.packages("tidytext", repos="http://cran.us.r-project.org")
}
library(textclean)
if (!require(udpipe)) {
  install.packages("udpipe", repos="http://cran.us.r-project.org")
}
library('udpipe')

if (!require("pacman")) install.packages("pacman")
pacman::p_load(sentimentr, dplyr, magrittr)
library('sentimentr')


ud_model <- udpipe_download_model(language = "english")
ud_model <- udpipe_load_model(ud_model$file_model)

working_dir = '/Users/michaeltauberg/projects/gizmodo/'
csv_name = "title_views.csv"
data_name = "gawker_titles_top1000"
setwd(working_dir)

dt = read.csv(csv_name)
  



## connect to db
#con = dbConnect(drv=RSQLite::SQLite(), dbname="gawker.sqlite")
#con = dbConnect(RSQLite::SQLite(), "gawker.sqlite")
#db = dbConnect(SQLite(), dbname="gawker.sqlite")

## list all tables
#tables = dbListTables(con)

################
# WORD CLOUDS
################
GenerateWordClouds <- function(dt, data_name, color) {
  dt$title = gsub('\'',"",as.character(dt$title))
  dt$title = gsub('\"',"",as.character(dt$title))
  dt$title = gsub('\'s',"",as.character(dt$title))
  
  dt_sent = unnest_tokens(dt, "sentences", title, token = "sentences")
  # only use sentences that contain the subject - ie "harris"
  subject_words = dt_sent$sentences
  subject_words = strip(subject_words, apostrophe.remove=TRUE)

  # # NLP
  x <- udpipe_annotate(ud_model, x = subject_words)
  x <- as.data.frame(x)
  # 
  # ## ADJECTIVES
  stats <- subset(x, upos %in% c("ADJ")) 
  stats <- txt_freq(stats$token)
  stats$key <- factor(stats$key, levels = rev(stats$key))
  # 
  boring_words = c('donald', 'other', 'josh')
  # 
  for (word in boring_words) {
     stats = stats[stats$key != word,]
  }
  stats = stats[1:25,]
  p = ggplot(stats, aes(x=key, y=freq, fill="blue")) + geom_bar(stat="identity") 
  p = p + ggtitle(sprintf("Most Common %s Adjectives", data_name))
  p = p + theme(plot.title = element_text(hjust = 0.5))
  p = p + theme(axis.text.x=element_text(angle=90, hjust=1,face="bold"))
  p = p + theme(axis.text=element_text(size=16,face="bold"), axis.title=element_text(size=13), axis.title.y=element_blank())
  p = p + theme(plot.title = element_text(size=14,face="bold"))
  p = p + xlab("Number of Occurances") + guides(fill=FALSE)
  p = p + coord_flip()
  p = p + scale_fill_manual(values = c(color)) + theme_classic()
  ggsave(filename = sprintf("./%s_adjectives.png", data_name) , plot=p, width=8, height=6)
   
  
  words = Corpus(VectorSource(subject_words))
  #words = Corpus(VectorSource(dt$title))
  
  corpus <- tm_map(words, content_transformer(tolower))
  
  words = tm_map(words, stripWhitespace)
  words = tm_map(words, tolower)
  
  complete_stopwords = c(stopwords('english'), "new", "will", "now", "like", "news", "day", "one", "two", "get", "gets", "still")
  complete_stopwords = c(complete_stopwords, "good", "make", "back", "says", "just", "watch", "week", "dont", "gawker", "cant")
  complete_stopwords = c(complete_stopwords, "wants", "can", "today", "night", "goes", "live", "real", "last", "another")
  complete_stopwords = c(complete_stopwords, "another", "know", "bad", "makes", "big")  
  
  # Generate wordcloud removing all stop words
  png(sprintf("./%s_stopwords_wordcloud.png", data_name))
  words = tm_map(words, removeWords, complete_stopwords)
  wordcloud(words, max.words = 50, min.freq=5, random.order=FALSE, colors=brewer.pal(8,"Dark2"))
  
  dev.off()
  
  dtm = TermDocumentMatrix(words)
  m = as.matrix(dtm)
  v = sort(rowSums(m),decreasing=TRUE)
  d = data.frame(word = rownames(m),
                 freq = rowSums(m),
                 row.names = NULL)
  #d = data.frame(word = names(v),freq=v)
  d = d[order(d$freq, decreasing=TRUE),]
  d$word = factor(d$word, levels = d$word[order(d$freq, decreasing=TRUE)])

  top_words = d[1:10,]
  p = ggplot(top_words, aes(x=word, y=freq, fill=data_name)) + geom_bar(stat="identity")
  p = p + ggtitle(sprintf("%s - Top Headline Words", toupper(data_name)))
  p = p + theme(plot.title = element_text(hjust = 0.5))
  p = p + theme(axis.text.x=element_text(angle=90, hjust=1,face="bold"))
  p = p + theme(axis.text=element_text(size=16,face="bold"), axis.title=element_text(size=13), axis.title.x=element_blank())
  p = p + theme(plot.title = element_text(size=18,face="bold"))
  #p = p + xlab("Word")
  p = p + scale_fill_manual(values = c(color)) + guides(fill=FALSE)
  p = p + ylab("Number of Uses") + theme_classic()

  #p = p + scale_y_continuous(limits = c(0, 1200)) + scale_x_continuous(limits = c(0, 1000))
  ggsave(filename = sprintf("./%s_top10_words.png", data_name) , plot=p, width=4.5, height=6)
}

dt = dt[order(dt$views, decreasing=TRUE),]
dt = dt[dt$title != "Front views",] # wrong value
dt = dt[1:1000,]

GenerateWordClouds(dt, data_name, "blue") 
hits = dt[dt$views> 1000000,]
GenerateWordClouds(hits, "hits", "black") 

hits$headline = as.character(hits$title)
hits_sentiment = sentiment(hits$headline)


dt$headline = as.character(dt$title)
dt_sentiment = sentiment(dt$headline)
