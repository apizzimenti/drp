
import pandas as pd

demographics = pd.read_csv("data/demographics/sc/block20.csv")
blackTOT = [c for c in list(demographics) if "BLACK" in c and "VAP" not in c]
blackVAP = [c for c in list(demographics) if "BLACK" in c and "VAP" in c]

demographics["APBPOP20"] = demographics[blackTOT].sum(axis=1)
demographics["APBVAP20"] = demographics[blackVAP].sum(axis=1)

keep = ["GEOID20", "TOTPOP20", "WHITEPOP20", "VAP20", "APBPOP20", "WHITEVAP20", "APBVAP20"]
demographics = demographics[keep]
demographics.to_csv("data/demographics/sc/block20-pared.csv", index=False)
