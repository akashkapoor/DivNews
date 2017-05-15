# Example usage: python cluster_elbow.py trump

import sys
import urllib
import twitter
from newspaper import Article, Source
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from scipy.spatial.distance import *
from Levenshtein import distance

# Min and max number of clusters to try:
min_cluster = 2;
max_cluster = 20;

length_threshold = 500;

# The threshold to use for ending the elbow method
# If the new number of clusters increases the total variance
# by less than this threshold, use the previous clustering
elbow_threshold = 0.5;

consumer_key = 'W1IDd26JcftYg0D0Auw7zZOq3';
consumer_secret = 'Mn4qP3EsDYL9brJ5CyNiXIq1oxFVfUejaZNC0kefu4555SLZGA';
access_token = '3415407254-BscF1KNbj6aLVwi6fGyt2D5VMOxhyMhWOPXyUi8';
access_secret = '4aTHwRWD9gJyHCZFzOuql4nPy41AtfVZC1bIgfxptwchk';

def tokenize(text):
	stemmer = PorterStemmer();
	return [stemmer.stem(word) for word in word_tokenize(text)];

def load_tweets(query):
	query = urllib.quote('\'' + query + '\'');
	api = twitter.Api(
		consumer_key=consumer_key, 
		consumer_secret=consumer_secret, 
		access_token_key=access_token, 
		access_token_secret=access_secret);
	tweets = api.GetSearch(
		raw_query="q=" + query + "&result_type=mixed&count=100&lang=en");
	return tweets;

def get_urls(tweets):
	tweets_url = [];
	urls = [];
	for tweet in tweets:
		if tweet.urls:
			url = tweet.urls[0].expanded_url;
			# Filter out non-news URLs
			if 'vine.' in url or 'youtu' in url or'fb.me' in url or 'https://twitter.com/' in url or 'https://www.instagram.com' in url: 
				continue;
			tweets_url.append(tweet);
			urls.append(url);
	return tweets_url, urls;

def load_articles(tweets_url, urls):
	articles = [];
	for url in urls:
		articles.append(Article(url=url));
	source = Source('https://');
	source.articles = articles;
	source.download_articles(threads=20);
	valid_tweets = [];
	valid_article = [];
	for i in range(len(articles)):
		articles[i].parse();
		if len(articles[i].text) >= length_threshold:
			valid_tweets.append(tweets_url[i]);
			valid_article.append(articles[i]);
	return valid_tweets, valid_article;

def extract_features(tweets_url, articles):
	all_texts = [];
	for i in range(len(articles)):
		all_texts.append(tweets_url[i].text + ' ' + articles[i].title + ' ' + articles[i].text);
	vectorizer = TfidfVectorizer(stop_words='english', tokenizer=tokenize, ngram_range=(1,2));
	bow_tfidf = vectorizer.fit_transform(all_texts);
	return bow_tfidf;

def cluster(bow, n_clusters):
	labels = KMeans(n_clusters=n_clusters, n_init=50, n_jobs=-1).fit(bow).labels_;
	var_list = [];
	for cluster_i in range(n_clusters):
		cluster_list = [i for i in range(len(labels)) if labels[i] == cluster_i];
		bow_cluster = bow[cluster_list];
		eucliean_distances = cdist(bow.toarray(),bow.toarray(),'seuclidean');
		var = sum(sum(eucliean_distances))/2.0/len(cluster_list);
		var_list.append(var);
	total_var = sum(var_list);
	return labels, total_var;

def elbow(bow):
	prev_labels = [];
	prev_var = 0;
	for n_clusters in range(min_cluster, max_cluster):
		labels, total_var = cluster(bow, n_clusters);
		if total_var <= prev_var * (1 + elbow_threshold):
			break;
		prev_var = total_var;
		prev_labels = labels;
	return prev_labels;

def display(tweets_url, labels):
	for i in range(max(labels) + 1):
		print '*'*100;
		print i;
		for j in range(len(labels)):
			if labels[j] == i:
				print tweets_url[j].text;
				print '_'*100;

query = sys.argv[1];
print "Loading tweets..."
tweets = load_tweets(query);
print str(len(tweets)) + ' tweets loaded.'
print "Extracting URLs..."
tweets, urls = get_urls(tweets);
print str(len(tweets)) + ' tweets with URL.'
print "Loading and parsing articles..."
tweets, articles = load_articles(tweets, urls);
print str(len(tweets)) + ' tweets with valid article.'
print "Extracting features..."
bow = extract_features(tweets, articles);
print "Clustering..."
labels = elbow(bow);
print str(max(labels) + 1) + ' clusters.'
display(tweets, labels);
