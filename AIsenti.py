from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
sia=SentimentIntensityAnalyzer()
e=1
while e!=0:
    text=input('enter a comment:')
    if text.strip():
        sentiment=sia.polarity_scores(text)
    

        if sentiment['compound'] >= 0.05:
            result='pogidinaduku thanks ra love you to'

        elif sentiment['compound'] <= -0.05:
            result='nanu tidutav ra chetana kodaka'

        else:
            result='ha manchidi'

        print(result)

    else:
        print('no comment entered')
