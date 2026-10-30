import pandas as pd

df = pd.read_csv("data/raw/playstore_reviews.csv")

print(df["label"].value_counts())
print("\nShare with exactly 0 polarity:", round((df["polarity"] == 0).mean(), 2))
print("\nAverage polarity by star rating:")
print(df.groupby("score")["polarity"].mean().round(2))

cols = ["score", "polarity", "content"]
print("\n--- 1-2 stars but TextBlob says positive ---")
print(df[(df.score <= 2) & (df.polarity > 0.2)][cols].head(8).to_string())

print("\n--- 4-5 stars but TextBlob says negative or neutral ---")
print(df[(df.score >= 4) & (df.polarity <= 0)][cols].head(8).to_string())