import pandas as pd

df = pd.read_csv("data/raw/playstore_reviews.csv", parse_dates=["at"])

monthly = (df.set_index("at")
             .resample("MS")
             .agg(reviews=("reviewId", "count"),
                  avg_stars=("score", "mean"),
                  avg_polarity=("polarity", "mean")))
print(monthly.round(2))

print("\nTop app versions by review count:")
print(df["reviewCreatedVersion"].value_counts().head(8))

print("\nAverage stars by app version (versions with 30+ reviews):")
by_version = (df.groupby("reviewCreatedVersion")
                .agg(reviews=("reviewId", "count"),
                     avg_stars=("score", "mean"))
                .query("reviews >= 30")
                .sort_values("reviews", ascending=False))
print(by_version.round(2))

v5 = df[df["reviewCreatedVersion"].astype(str).str.startswith("5")]
print("\nVersion 5.x (the new app):")
print(v5.groupby("reviewCreatedVersion")
        .agg(reviews=("reviewId", "count"), avg_stars=("score", "mean"),
             first_seen=("at", "min"))
        .sort_values("first_seen").round(2).to_string())