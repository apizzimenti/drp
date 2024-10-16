from gerrychain import Partition, Graph, MarkovChain, updaters, constraints, accept, Election
from gerrychain.proposals import recom, propose_random_flip
from gerrychain.constraints import contiguous, single_flip_contiguous
from gerrychain.tree import recursive_seed_part
from functools import partial
from gerrytools.scoring import *
import random
import matplotlib.pyplot as plt
import numpy as np

# Column names
POPULATION = "TOTPOP20"
N = 100
election = Election("USS22", {"Dem": "22GUSSD", "Rep": "22GUSSR"})
# elections = ["PRES12", "SEN12", "USH12", 
            #  "GOV14", "AG14", "COMP14", "USH14", "SSEN14", 
            #  "PRES16", "SEN16", "USH16",
            #  "GOV18", "SEN18", "USH18", "AG18", "COMP18", "SSEN18"]

# Import graph; specify updaters.
G = Graph.from_json("./data/graphs/sc/SC-VTD20.json")
updaters = {
    POPULATION: updaters.Tally(POPULATION, POPULATION),
    "USS22": election
}
updaters.update(demographic_updaters(["TOTPOP20", "VAP20", "APBVAP20"]))

ideal = sum(data[POPULATION] for _, data in G.nodes(data=True))/7
partition = recursive_seed_part(G, range(7), ideal, POPULATION, 0.05)
for v, data in G.nodes(data=True): 
    data["INITIAL"] = partition[v]

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

# Initial APB demographic shares
apb_scores = demographic_shares({"VAP20": ["APBVAP20"]})
apb_tally = summarize(initial, apb_scores)
print(apb_tally)


assignment_list = [initial] # List to collect MC steps
for (i, initial) in enumerate(M):
    print(f"Step {i} Republican vote share for district 1: "
          f"{initial['USS22'].percents('Rep')[1]:0.4f}")
    apb_scores = demographic_shares({"VAP20": ["APBVAP20"]})
    apb_tally = summarize(initial, apb_scores)
    print(apb_tally['APBVAP20_share'][1])

    # Markov comparison 
    rep_shares_i = assignment_list[-1]['USS22'].percents('Rep')[1]
    rep_shares_f = initial['USS22'].percents('Rep')[1]
    apb_shares_i = summarize(assignment_list[-1], apb_scores)
    apb_shares_f = summarize(initial, apb_scores)

    # Two factors in the number for comparison: prioritizing republican tilt and high APB share 
    markov = float((rep_shares_f/rep_shares_i)) 
    markov *= (float(apb_shares_f['APBVAP20_share'][1])/float(apb_shares_i['APBVAP20_share'][1]))
    

    if markov >= 1:
        assignment_list.append(initial)
        
    else: 
        alpha = random.random()
        if alpha <= markov:
            assignment_list.append(initial)

# plot the points in the markov chain 
xpts = [] #APBVAP share
ypts = [] #Republican tilt as of Senate election 2022
for plan in assignment_list:
    apb_share = summarize(plan, apb_scores)
    xpts.append(apb_share['APBVAP20_share'][1])
    ypts.append(plan['USS22'].percents('Rep')[1])

apb_share = np.array(xpts)
rep_share = np.array(ypts)

plt.plot(apb_share, rep_share, 'o')
plt.show()
