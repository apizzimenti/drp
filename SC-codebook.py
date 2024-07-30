
import json

book = {}

electioncodes = {
    "AGR": "AGR",
    "ATG": "ATG",
    "COM": "COM",
    "GOV": "GOV",
    "SOS": "SOS",
    "SUP": "EDU",
    "TRE": "TRE",
    "USS": "USS",
    "CON": "USH",
    "SL": "SLL"
}

elections = set(electioncodes.keys())
districted = {"CON", "SL"}

with open("sc-election-codebook.txt") as r:
    for line in r:
        _oldcode = line.split()[0]
        oldcode = _oldcode[:7]
        party = oldcode[-1]
        newcode = "22G"

        for election in elections:
            if election in oldcode:
                newcode += electioncodes[election]
                if election in districted:
                    district = oldcode[3:6] if election == "SL" else oldcode[4:6]
                    newcode += district

        newcode += party
        book[_oldcode] = newcode

with open("sc-gen22-codebook.json", "w") as w:
    json.dump(book, w, indent=2)
