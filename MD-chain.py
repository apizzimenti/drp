from gerrychain import Partition, Graph, MarkovChain, updaters, constraints, accept, Election
from gerrychain.proposals import recom, propose_random_flip
from gerrychain.constraints import contiguous, single_flip_contiguous
from gerrychain.tree import recursive_seed_part
from functools import partial
from gerrytools.scoring import *
import random

# Column names. Hi Grace!
POPULATION = "TOTPOP20"
N = 100
elections = ["PRES12", "SEN12", "USH12", 
             "GOV14", "AG14", "COMP14", "USH14", "SSEN14", 
             "PRES16", "SEN16", "USH16",
             "GOV18", "SEN18", "USH18", "AG18", "COMP18", "SSEN18"]

# Import graph; specify updaters.
G = Graph.from_json("./data/graphs/md/MD-VTD20.json")
updaters = {
    POPULATION: updaters.Tally(POPULATION, POPULATION)
}
# add elections to updaters
for race in elections:
    updaters[race] = Election(race, {"Dem": race + "D", "Rep": race+"R"})
updaters.update(demographic_updaters(["TOTPOP20", "VAP20", "BVAP20", "HVAP20", "WVAP20", "ASIANVAP20"]))


ideal = sum(data[POPULATION] for _, data in G.nodes(data=True))/8
partition = recursive_seed_part(G, range(8), ideal, POPULATION, 0.05)
for v, data in G.nodes(data=True): data["INITIAL"] = partition[v]

initial = Partition(G, "INITIAL", updaters)

proposal = partial(
    recom,
    pop_col=POPULATION,
    pop_target=ideal,
    epsilon=0.05
)

M = MarkovChain(
    proposal,
    constraints=[contiguous],
    accept=accept.always_accept,
    initial_state=initial,
    total_steps=N
)

# for assignment in M:
#     print(assignment)

i = 1
# for partition in M:
#     print(f"Step {i} population for district 1: {partition['population'][1]}")
#     i += 1

ginglesSummary = {}
for n in range(0, 9):
    ginglesSummary[n] = 0

assignment_list = [initial]
for i, item in enumerate(M):
    # print(f"Finished step {i+1}/{len(M)}", end="\r")
    
    # print(item[POPULATION])
    # print(seats(elections, "Dem").apply(item))

    # share_scores = demographic_shares({"VAP20": ["BVAP20", "HVAP20"]})
    # share_dictionary = summarize(item, share_scores)
    # print(share_dictionary)

    # tally_scores = demographic_tallies(["BVAP20"])
    # tally_dictionary = summarize(item, tally_scores)
   

    gScores = gingles_districts({"VAP20": ["BVAP20"]}, threshold = 0.5)
    gPlanF = summarize(item, gScores)
    gNumF = gPlanF['BVAP20_gingles_districts'] #number of gingles districts in proposed plan
    gPlanI = summarize(assignment_list[-1], gScores)
    gNumI = gPlanI['BVAP20_gingles_districts'] #number of gingles districts in original plan
    # accounts for if there are 0 initial gingles districts
    if gNumF >= gNumI:
        assignment_list.append(item)
        ginglesSummary[gNumF] += 1
    else: 
        acceptanceRate = gNumF/gNumI
        alpha = random.random()
        if alpha <= acceptanceRate:
            assignment_list.append(item)
            ginglesSummary[gNumF] += 1

# print(ginglesSummary)
for key, value in ginglesSummary.items():
    print(f"{key} gingles district: {value} plans")