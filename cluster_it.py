# Example usage: python cluster_elbow.py trump
import json
import sys
import urllib
import twitter
from newspaper import Article, Source
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering, AffinityPropagation
from scipy.spatial.distance import *
from scipy.sparse import hstack, vstack
from Levenshtein import distance
import re

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

def remove_url(text):
	return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text).strip();

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
            if 'www.snapchat.com' in url or 'vine.' in url or 'youtu' in url or'fb.me' in url or 'https://twitter.com/' in url or 'https://www.instagram.com' in url: 
                continue;
            tweets_url.append(tweet);
            urls.append(url);
    return tweets_url, urls;

def load_articles(tweets, urls):
    articles = [];
    for url in urls:
        articles.append(Article(url=url));
    source = Source('https://');
    source.articles = articles;
    source.download_articles(threads=20);
    valid_tweets = [];
    valid_article = [];
    print "Parsing articles..."
    for i in range(len(articles)):
    	if not articles[i].html:
    		continue;
        articles[i].parse();
        if len(articles[i].text) >= length_threshold:
            valid_tweets.append(tweets[i]);
            valid_article.append(articles[i]);
    return valid_tweets, valid_article;

def extract_features(tweets, articles):
    all_texts = [];
    for i in range(len(articles)):
        all_texts.append(tweets[i].text + ' ' + articles[i].title + ' ' + articles[i].text);
    vectorizer = TfidfVectorizer(stop_words='english', tokenizer=tokenize, ngram_range=(1,2));
    bow = vectorizer.fit_transform(all_texts);
    return bow;

def cluster(bow, n_clusters, algo):
    if algo == 0:
        clt = KMeans(n_clusters=n_clusters, n_init=50, n_jobs=-1);
        labels = clt.fit(bow).labels_;
    elif algo == 1:
        clt = AgglomerativeClustering(n_clusters=n_clusters);
        labels = clt.fit(bow.toarray()).labels_;
    else:
        return;
    var_list = [];
    for cluster_i in range(n_clusters):
        cluster_list = [i for i in range(len(labels)) if labels[i] == cluster_i];
        bow_cluster = bow[cluster_list];
        eucliean_distances = cdist(bow.toarray(),bow.toarray(),'seuclidean');
        var = sum(sum(eucliean_distances))/2.0/len(cluster_list);
        var_list.append(var);
    total_var = sum(var_list);
    return labels, total_var;

def elbow(bow, algo):
    prev_labels = [];
    prev_var = 0;
    for n_clusters in range(min_cluster, max_cluster):
        if n_clusters > bow.shape[0]:
            break;
        labels, total_var = cluster(bow, n_clusters, algo);
        if total_var <= prev_var * (1 + elbow_threshold):
            break;
        prev_var = total_var;
        prev_labels = labels;
    return prev_labels;

def affinity_propagation(bow):
	clt = AffinityPropagation();
	clt.fit(bow);
	return clt.labels_;

def display(tweets, labels):
    for i in range(max(labels) + 1):
        print '*'*100;
        print i;
        for j in range(len(labels)):
            if labels[j] == i:
                print tweets[j].text;
                print '_'*100;

def tweet_to_dict(tweet, article):
	tweet_dict = {};
	if article.top_img:
		tweet_dict["img"] = article.top_img;
	else:
		tweet_dict["img"] = 'https://pbs.twimg.com/profile_images/685545181328756736/xYRETZ4f.png';
	tweet_dict["name"] = tweet.user.name;
	tweet_dict["handle"] = tweet.user.screen_name;
	tweet_dict["date"] = tweet.created_at;
	tweet_dict["text"] = tweet.text;
	return tweet_dict;

def find_center(bow):
	centroid = sum(bow);
	center_i = -1;
	min_dist = 2;
	for i in range(len(bow)):
		v = bow[i];
		dist = cosine(centroid, v);
		if dist < min_dist:
			min_dist = dist;
			center_i = i;
	return i;

def tweet_dedup(tweet_dicts):
	dedup_tweets = [];
	for tweet_dict in tweet_dicts:
		for exist_tweet in dedup_tweets:
			if distance(remove_url(tweet_dict["text"]), remove_url(exist_tweet["text"])) < 20:
				break;
		else:
			dedup_tweets.append(tweet_dict);
	return dedup_tweets;

def clusters_to_dict(tweets, labels, articles, bow):
	cluster_dicts = [];
	for label in range(max(labels) + 1):
		cluster_dict = {};
		tweet_dicts = [];
		index_cluster = [];
		bow_cluster = [];
		for i in range(len(labels)):
			if labels[i] == label:
				tweet_dicts.append(tweet_to_dict(tweets[i], articles[i]));
				index_cluster.append(i);
				bow_cluster.append(bow[i]);
		bow_cluster = vstack(bow_cluster).toarray();
		center_index = index_cluster[find_center(bow_cluster)];
		tweet_dicts = tweet_dedup(tweet_dicts);
		cluster_dict["tweets"] = tweet_dicts;
		centroid_tweet = tweets[center_index];
		centroid_article = articles[center_index];
		if len(centroid_article.summary) == 0:
			centroid_article.nlp();
		if centroid_article.top_img:
			cluster_dict["main_img"] = centroid_article.top_img;
		else:
			cluster_dict["main_img"] = 'https://pbs.twimg.com/profile_images/685545181328756736/xYRETZ4f.png';
		cluster_dict["tweet_text"] = centroid_tweet.text;
		cluster_dict["headline"] = centroid_article.title;
		cluster_dict["summary"] = centroid_article.summary;
		cluster_dicts.append(cluster_dict);
	return cluster_dicts;

def do_it(query):
    # query = sys.argv[1];
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
    labels_kmeans = elbow(bow, 0);
    labels_aggl = elbow(bow, 1);
    labels_aff = affinity_propagation(bow);
    cluster_dicts_kmeans = clusters_to_dict(tweets, labels_kmeans, articles, bow);
    cluster_dicts_aggl = clusters_to_dict(tweets, labels_aggl, articles, bow);
    cluster_dicts_aff = clusters_to_dict(tweets, labels_aff, articles, bow);
    jsonHead = {};
    jsonHead["kmeans"] = cluster_dicts_kmeans;
    jsonHead["aggl"] = cluster_dicts_aggl;
    jsonHead["aff"] = cluster_dicts_aff;
    jstr = 'var data = ' + json.dumps(jsonHead)
    with open('result2.json', 'w') as fp:
        fp.write(jstr)
    return jsonHead
    # #return json.dumps(jsonHead, indent=4)
    # with open('result2.json', 'w') as fp:
    #     json.dump(jsonHead, fp, indent=4);
    # return "done"


#print do_it(sys.argv[1])
