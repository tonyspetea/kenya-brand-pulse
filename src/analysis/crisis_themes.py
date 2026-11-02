import re
from collections import Counter
import pandas as pd
import warnings
warnings.filterwarnings("ignore", message="This pattern is interpreted")

df = pd.read_csv("data/raw/playstore_reviews.csv", parse_dates=["at"])
df["content"] = df["content"].fillna("").astype(str).str.lower()

neg = df[df["score"] <= 2]
crisis = neg[(neg["at"] >= "2026-04-01") & (neg["at"] < "2026-07-01")]
base = neg[(neg["at"] >= "2025-10-01") & (neg["at"] < "2026-04-01")]
print(f"1-2 star reviews: crisis (Apr-Jun 2026) = {len(crisis)}, baseline (Oct 2025-Mar 2026) = {len(base)}")

STOP = set("""the and for that this with you are was not but have has had they them their its it's
i'm i've don't can't just very too all any can will would could should from your our out get got
app mpesa m-pesa safaricom please like one now when what why how who been being were than then
there here also only more much even still really because about into over after before again""".split())

def tokens(t):
    return re.findall(r"[a-z']+", t)

def share_counts(texts):
    uni, bi = Counter(), Counter()
    for t in texts:
        w = tokens(t)
        uni.update({x for x in w if x not in STOP and len(x) > 2})
        bi.update({f"{a} {b}" for a, b in zip(w, w[1:]) if a not in STOP and b not in STOP})
    return uni, bi

def lift_table(c_counts, b_counts, n_c, n_b, min_count=30, top=20):
    rows = []
    for term, c in c_counts.items():
        if c < min_count:
            continue
        cs, bs = c / n_c, b_counts.get(term, 0) / n_b
        rows.append((term, c, round(100 * cs, 1), round(100 * bs, 1), round((cs + 0.002) / (bs + 0.002), 1)))
    out = pd.DataFrame(rows, columns=["term", "crisis_n", "crisis_%", "base_%", "lift"])
    return out.sort_values("lift", ascending=False).head(top)

cu, cb = share_counts(crisis["content"])
bu, bb = share_counts(base["content"])

print("\nWords that jumped most (share of reviews mentioning them):")
print(lift_table(cu, bu, len(crisis), len(base)).to_string(index=False))
print("\nTwo-word phrases that jumped most:")
print(lift_table(cb, bb, len(crisis), len(base), min_count=20).to_string(index=False))

themes = {
    "can't log in / won't open / crashes": r"log ?in|sign ?in|can'?t open|won'?t open|crash|hang|stuck|loading|not working|doesn'?t work",
    "prefers the old version":              r"old (version|app)|previous|bring back|revert|go back",
    "update / new version":                 r"updat|new version|latest",
    "missing features / bundles / airtime": r"missing|where is|no longer|removed|can'?t find|bundle|airtime",
    "slow / lagging":                       r"slow|lag|takes (so )?long|delay",
    "hard to use":                          r"complicated|confusing|user.?friendly|difficult|hard to",
    "PIN / OTP / SIM / verification":       r"\bpin\b|fingerprint|biometric|otp|verif|\bsim\b",
    "fees / charges":                       r"charge|fee|cost|expensive",
    "needs mobile data / wifi / roaming":   r"wi-?fi|mobile data|switch(?:ing)? network|roaming|buy bundles",
    "forced migration / no choice":         r"forced|no option|option to choose|separate|oneapp",
    "intrusive features (Zuri)":            r"zuri",
    "lost data / removed features":         r"\blost\b|disappear|gone|removed|no longer",
}
rows = []
for name, pat in themes.items():
    c = crisis["content"].str.contains(pat, regex=True).mean() * 100
    b = base["content"].str.contains(pat, regex=True).mean() * 100
    rows.append((name, round(b, 1), round(c, 1)))
print("\nTheme share of 1-2 star reviews (%):")
theme_df = pd.DataFrame(rows, columns=["theme", "baseline_%", "crisis_%"])
print(theme_df.to_string(index=False))
theme_df.to_csv("docs/crisis_theme_shares.csv", index=False)
print("\nMost-upvoted crisis reviews (others agreed with these):")
top = crisis.sort_values("thumbsUpCount", ascending=False).head(8)
for _, r in top.iterrows():
    print(f"\n[{r['thumbsUpCount']} upvotes, {r['score']} stars, {r['at'].date()}]\n{r['content'][:300]}")