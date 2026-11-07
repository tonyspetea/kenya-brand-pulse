import warnings
from pathlib import Path
import pandas as pd

warnings.filterwarnings("ignore", message="This pattern is interpreted")

df = pd.read_csv("data/raw/playstore_reviews.csv", parse_dates=["at"])
df["content"] = df["content"].fillna("").astype(str)
text = df["content"].str.lower()

# time and grouping columns
df["date"] = df["at"].dt.date
df["month"] = df["at"].dt.to_period("M").dt.to_timestamp()
df["period"] = pd.cut(df["at"],
    [pd.Timestamp("2000-01-01"), pd.Timestamp("2026-04-01"), pd.Timestamp("2026-07-01"), pd.Timestamp("2100-01-01")],
    labels=["1 Before change", "2 Crisis (Apr-Jun 2026)", "3 Recovery (Jul 2026 on)"], right=False)

# sentiment: stars are the more reliable signal, TextBlob kept for comparison
df["rating_band"] = pd.cut(df["score"], [0, 2, 3, 5], labels=["Negative", "Neutral", "Positive"])
df["polarity_label"] = pd.cut(df["polarity"], [-1.01, -0.1, 0.1, 1.01],
                              labels=["Negative", "Neutral", "Positive"])
df["app_major"] = ("v" + df["reviewCreatedVersion"].astype(str).str.split(".").str[0]).replace("vnan", "Unknown")

# complaint themes as 0/1 flags, so Power BI can trend them by month
themes = {
    "theme_login":             r"log ?in|sign ?in|can'?t open|won'?t open|crash|hang|stuck|loading|not working|doesn'?t work",
    "theme_old_version":       r"old (version|app)|previous|bring back|revert|go back|downgrade",
    "theme_update":            r"updat|upgrade|new version|latest",
    "theme_missing_features":  r"missing|where is|can'?t find|bundle|airtime",
    "theme_slow":              r"slow|sluggish|lag|takes (so )?long|delay",
    "theme_hard_to_use":       r"complicated|confusing|user.?friendly|difficult|hard to|messy",
    "theme_verification":      r"\bpin\b|fingerprint|biometric|otp|verif|\bsim\b",
    "theme_fees":              r"charge|fee|cost|expensive",
    "theme_wifi_data":         r"wi-?fi|mobile data|switch(?:ing)? network|roaming|buy bundles",
    "theme_forced_migration":  r"forced|no option|option to choose|separate|oneapp",
    "theme_lost_data":         r"\blost\b|disappear|\bgone\b|removed|no longer",
}
for col, pat in themes.items():
    df[col] = text.str.contains(pat, regex=True).astype(int)

out = Path("data/powerbi"); out.mkdir(parents=True, exist_ok=True)

fact_cols = (["reviewId", "brand", "date", "month", "period", "score", "rating_band",
              "polarity", "polarity_label", "thumbsUpCount", "reviewCreatedVersion", "app_major"]
             + list(themes))
df[fact_cols].rename(columns={"reviewId": "review_id", "thumbsUpCount": "thumbs_up",
                              "reviewCreatedVersion": "app_version"}
                     ).to_csv(out / "reviews_fact.csv", index=False)

# review text kept in its own file so you decide whether it ever leaves your machine
df[["reviewId", "content"]].rename(columns={"reviewId": "review_id"}
                                   ).to_csv(out / "reviews_text.csv", index=False)

print("fact rows:", len(df), "| theme columns:", len(themes))
print(df.groupby("period", observed=True)[["score"]].agg(["count", "mean"]).round(2))