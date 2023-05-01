from flask import Flask, render_template , redirect, url_for, request
import tweepy
from textblob import TextBlob
#from wordcloud import WordCloud
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def home():
    return render_template('index.html')

@app.route('/result',methods=['POST','GET'])
def result():
    if request.method=="POST":
        uname=request.form.get("username")
        #my twitter development account credentials
        consumerKey="PP1I4Ueqd7taKjiuJ3RTz7fdx"
        consumerSecret="NbMakl8AXjVckB2EDCywWG1riKDeqoYkGSnKdG8B7BbfoEEdtU"
        accessToken="1579176161695129600-vUe3KPvsTtrCaSD1ORJ7j8wnxP492D"
        accessTokenSecret="L75kUQj4gWHdTWNn5a2Hdw0zLmMJpCssNoUwvOjmNBhNJ"

        #creating the authentication object
        authenticate=tweepy.OAuthHandler(consumerKey,consumerSecret)
        #setting the access token and access token secret
        authenticate.set_access_token(accessToken,accessTokenSecret)
        #creating the API object while passing the authentication information
        api=tweepy.API(authenticate,wait_on_rate_limit=True)


        #extracting 100 tweets from the twitter user
        posts=api.user_timeline(screen_name=uname,count=100,lang="en", tweet_mode="extended")


        #creating a dataframe with a column called Tweets
        df=pd.DataFrame([tweet.full_text for tweet in posts],columns=['Tweets'])


        #cleaning the tweets for mentions, hashtags and urls
        def cleanTxt(text):
            text=re.sub(r'@[_A-Za-z0-9]+','',text) #removed @mentions
            text=re.sub(r'#','',text) #removed '#' symbol
            text=re.sub(r'RT[\s]+','',text) #removed re tweets
            text=re.sub(r'https?:\/\/\S+','',text) #removed urls
            return text

        df['Tweets']=df['Tweets'].apply(cleanTxt)
        

        #create a function to get subjectivity of the tweets
        def getSubjectivity(text):
            return TextBlob(text).sentiment.subjectivity
        #create a function to get the polarity
        def getPolarity(text):
            return TextBlob(text).sentiment.polarity
        #creating two new columns in the dataframe
        df['Subjectivity']=df['Tweets'].apply(getSubjectivity)
        df['Polarity']=df['Tweets'].apply(getPolarity)
        

        #creating a function to compute the negative,neutral and positive analysis
        def getAnalysis(score):
            if (score<0 and score>=-0.5):
                return 'Fairly Negative'
            elif (score<-0.5 and score>=-1):
                return 'Strongly Negative'
            elif (score==0):
                return 'Neutral'
            elif (score>0 and score<=0.5):
                return 'Fairly Positive'
            else:
                return 'Strongly Positive'

        df['Analysis']=df['Polarity'].apply(getAnalysis)
        

        sub=df['Subjectivity'].tolist()
        pol=df['Polarity'].tolist()


        #plotting the polarity and subjectivity
        plt.figure(figsize=(10,10))
        for i in range(0,df.shape[0]):
            plt.scatter(df['Polarity'][i],df['Subjectivity'][i],color='Red')

        #plt.scatter(sub,pol)
        plt.title('Sentiment Analysis')
        plt.xlabel('Polarity')
        plt.ylabel('Subjectivity')
        plt.savefig('static/pvs.png',dpi=300)


        #showing the value counts
        df['Analysis'].value_counts()
        #plotting and visualizing the counts
        plt.figure(figsize=(10,10))
        plt.title('Sentiment Analysis')
        plt.xlabel('Sentiment')
        plt.ylabel('Counts')
        df['Analysis'].value_counts().plot(kind='bar')
        plt.savefig('static/bar.png',dpi=300)

        return render_template('result.html')

if __name__ == '__main__':
    app.run(debug="true")
