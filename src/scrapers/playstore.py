import time
import pandas as pd
from google_play_scraper import reviews, Sort
from textblob import TextBlob

# Find an app's ID in its Play Store URL: ...details?id=THIS_PART
APPS = {
    "M-PESA": "com.safaricom.mpesa.lifestyle",  # verify the ID in the URL
    # "KCB": "...", "Equity": "...",  add more here
}

def scrape(brand, app_id, n=315000):
    all_rows, token = [], None
    while len(all_rows) < n:
        rows, token = reviews(app_id, lang="en", country="ke",
                              sort=Sort.NEWEST, count=200,
                              continuation_token=token)
        if not rows:
            break
        all_rows += rows
        time.sleep(1)  # be polite to the server
    cols = ["reviewId", "content", "score", "thumbsUpCount", "at",
            "reviewCreatedVersion"]
    df = pd.DataFrame(all_rows).reindex(columns=cols)
    df["brand"] = brand
    return df

def add_sentiment(df):
    df["polarity"] = df["content"].apply(lambda t: TextBlob(str(t)).sentiment.polarity)
    df["label"] = pd.cut(df["polarity"], [-1.01, -0.1, 0.1, 1.01],
                         labels=["negative", "neutral", "positive"])
    return df

if __name__ == "__main__":
    frames = [scrape(b, i) for b, i in APPS.items()]
    df = add_sentiment(pd.concat(frames, ignore_index=True))
    df.to_csv("data/raw/playstore_reviews.csv", index=False)
    print(df.groupby("brand")["polarity"].describe())
    print("Correlation with star rating:", df["polarity"].corr(df["score"]))