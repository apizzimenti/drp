
from gerrychain import Partition, Graph, MarkovChain, updaters, constraints, accept
from gerrychain.proposals import recom
from gerrychain.constraints import contiguous
from gerrychain.tree import recursive_seed_part
from functools import partial

# Column names. Hi Grace!
POPULATION = "TOTPOP20"
N = 10

# Import graph; specify updaters.
G = Graph.from_json("./data/graphs/md/MD-VTD20.json")
updaters = {
    POPULATION: updaters.Tally(POPULATION, POPULATION)
}

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

for assignment in M:
    print(assignment)

