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
N = 10
election = ['22GUSS', '22GEDU', '22GGOV']
# elections = ["PRES12", "SEN12", "USH12", 
            #  "GOV14", "AG14", "COMP14", "USH14", "SSEN14", 
            #  "PRES16", "SEN16", "USH16",
            #  "GOV18", "SEN18", "USH18", "AG18", "COMP18", "SSEN18"]

# Import graph; specify updaters.
G = Graph.from_json("./data/graphs/sc/SC-VTD20.json")
updaters = {
    POPULATION: updaters.Tally(POPULATION, POPULATION),
    # "22GUSS": Election("22GUSS", {"Dem": "22GUSSD", "Rep": "22GUSSR"})
}
for e in election:
    updaters[e] = Election(e, {"Dem": e+"D", "Rep": e+"R"})
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
    # print(f"Step {i} Republican vote share for district 1: "
    #       f"{initial['USS22'].percents('Rep')[0]:0.4f}")
    print(f"Step {i} Republican seats: "
        f"{seats(election, 'Rep').apply(initial)}")
        
    apb_scores = demographic_shares({"VAP20": ["APBVAP20"]})
    apb_tally = summarize(initial, apb_scores)
    print(apb_tally['APBVAP20_share'][0])

    # Markov comparison 
    markov = 1
    for elect, seatNum in seats(election, 'Rep').apply(initial): # considers all elections in the markov comparison
        rep_seats_i = seats(election, 'Rep').apply(assignment_list[-1])[elect]
        rep_seats_f = seatNum
        markov *= float(rep_seats_f/rep_seats_i)
    
    apb_shares_i = summarize(assignment_list[-1], apb_scores)
    apb_shares_f = summarize(initial, apb_scores)

    # second factor: APB share  
    markov *= (float(apb_shares_f['APBVAP20_share'][1])/float(apb_shares_i['APBVAP20_share'][1]))
    

    if markov >= 1:
        assignment_list.append(initial)
        
    else: 
        alpha = random.random()
        if alpha <= markov:
            assignment_list.append(initial)

