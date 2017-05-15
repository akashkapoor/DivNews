import json

def get_tweet(user_img=None, userName=None, userHandle=None, dateTime=None, tweetText=None):
    tweet = {}
    tweet["img"] = "https://pbs.twimg.com/profile_images/714946924105883648/4fgNVF4H_normal.jpg"
    tweet["name"] = "Bloomberg"
    tweet["handle"] = "business"
    tweet["date"] = "Thu May 11 2017"
    tweet["text"] = "British Labour Partyu2019s manifesto has been leaked, revealing plans to nationalize railways"
    return tweet

def get_cluster(img=None, twt_txt=None, headline=None, summary=None, twt_lst=None):
    cluster = {}
    cluster["main_img"] = "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/iFf9oKDBfSMU/v0/1200x-1.jpg"
    cluster["tweet_text"] = "Memo from Justice Dept laying out rationale for Trump firing of Comey criticized his handling of last year investigation into Clinton email arrangement."
    cluster["headline"] = "After Comey, Justice Must Be Served"
    cluster["summary"] = "Congress needs to get serious about holding the president accountable."
    cluster["tweets"] = [
        get_tweet(), 
        get_tweet(),
        get_tweet(),
        get_tweet(),
        get_tweet(),
        get_tweet(),
        get_tweet()]
    return cluster


lst = []
for i in range(5):
    lst.append(get_cluster())


with open('result.json', 'w') as fp:
    jsonHead={}
    jsonHead["clusters"] = lst
    # Only get the JSON string
    jsonString = json.dumps(jsonHead)
    return jsonString

    # Saves to File
    #json.dump(clusters, fp, indent=4)






