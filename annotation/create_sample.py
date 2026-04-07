import pandas as pd
import random

random.seed(42)

df = pd.read_csv(
    "/root/cs496-codeswitching/data/arabizi-wanlp/words_annotated.csv"
    if __import__('os').path.exists("/root/cs496-codeswitching/data/arabizi-wanlp/words_annotated.csv")
    else str(__import__('pathlib').Path.home() / "cs496-codeswitching/data/arabizi-wanlp/words_annotated.csv")
)

LABEL_MAP = {1: "EN", 2: "AR", 3: "AR-LAT", 4: "FR", 5: "OTHER"}
df["label"] = df["categ"].map(LABEL_MAP)

# Keep only sentences that contain Arabizi (categ=3) or Arabic (categ=2)
# i.e. actual code-switching sentences
cs_sen_ids = df[df["categ"].isin([2, 3])]["sen_id"].unique()
print(f"Total code-switching sentences found: {len(cs_sen_ids)}")

# Sample 250 unique sentences
sampled_ids = random.sample(list(cs_sen_ids), min(250, len(cs_sen_ids)))
sampled = df[df["sen_id"].isin(sampled_ids)].copy()

# Build output
rows = []
for sen_id in sampled_ids:
    sen_tokens = sampled[sampled["sen_id"] == sen_id].reset_index(drop=True)
    for tok_id, row in sen_tokens.iterrows():
        rows.append({
            "sentence_id": sen_id,
            "token_id": tok_id + 1,
            "token": row["token"],
            "source_label": row["label"],
            "annotator_1": "",
            "annotator_2": "",
            "annotator_3": ""
        })

out = pd.DataFrame(rows)
out_path = str(__import__('pathlib').Path.home() / "cs496-codeswitching/annotation/annotation_sample.csv")
out.to_csv(out_path, index=False)
print(f"Saved {len(out)} tokens from {len(sampled_ids)} sentences")
print(f"Output: {out_path}")
print("\nLabel distribution in sample:")
print(out["source_label"].value_counts())
