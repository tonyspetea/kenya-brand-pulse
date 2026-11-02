import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df = pd.read_csv("data/raw/playstore_reviews.csv", parse_dates=["at"])
m = (df.set_index("at").resample("MS")
       .agg(reviews=("reviewId", "count"), avg_stars=("score", "mean")))
m = m.iloc[1:]  # drop the partial first month

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                               gridspec_kw={"height_ratios": [3, 1]})
ax1.plot(m.index, m["avg_stars"], marker="o", linewidth=2)
ax1.axvline(pd.Timestamp("2026-04-01"), linestyle="--", color="red")
ax1.annotate("Apr 2026: average rating falls to 2.1",
             xy=(pd.Timestamp("2026-04-01"), 2.09),
             xytext=(pd.Timestamp("2024-01-01"), 2.6),
             arrowprops=dict(arrowstyle="->"))
ax1.set_ylim(1.5, 5)
ax1.set_ylabel("Average stars")
ax1.set_title("M-PESA app (Google Play, Kenya): monthly average rating")
ax2.bar(m.index, m["reviews"], width=20)
ax2.set_ylabel("Reviews")

plt.tight_layout()
Path("docs").mkdir(exist_ok=True)
plt.savefig("docs/mpesa_rating_timeline.png", dpi=150)
print("saved docs/mpesa_rating_timeline.png")