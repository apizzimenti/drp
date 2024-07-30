
import pandas as pd

statewide = pd.read_csv("data/demographics/sc/precinct20-aggregated.csv")

# Assert some things about vote totals. If this completes without throwing an
# error, 
elections = [c for c in list(statewide) if "22g" in c.lower()]
POP = "TOTPOP20"
VAP = "VAP20"
ID = "GEOID20"

for election in elections:
    for population in [POP, VAP]:
        for _, row in statewide.iterrows():
            try:
                assert row[election] <= row[population]
            except:
                print(int(row[ID]))
                print(election, population)
                print(row[election], row[population])
                print()
