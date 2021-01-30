# Definition of the region automaton
from interval import constraint_subset

class RegionAutomaton(object):
    def __init__(self, name="", region_alphabet={}, locations=[], trans=[], initstate_names=[], accept_names=[]):
        self.name = name
        self.region_alphabet = region_alphabet
        self.locations = locations
        self.trans = trans
        self.initstate_names = initstate_names
        self.accept_names = accept_names
    
    def show(self):
        print("RegionAutomaton name: ")
        print(self.name)
        print("region alphabet: ")
        for untime_action in self.region_alphabet:
            print(untime_action)
            print([regionlabel.region.show() for regionlabel in self.region_alphabet[untime_action]])
        print("Location (name, init, accept, sink)")
        for l in self.locations:
            print(l.name, l.init, l.accept, l.sink)
        print("transitions: (id, source, label, target, timedlabel, symbolic_action): ")
        for t in self.trans:
            regions = []
            for num in t.alphabet_indexes:
                regions.append(self.region_alphabet[t.label][num].region)
            print(t.idx, t.source, t.label, t.target, regions, [t.label + "_" + str(num) for num in t.alphabet_indexes])
        print("init state: ")
        print(self.initstate_names)
        print("accept states: ")
        print(self.accept_names)

class RATran(object):
    def __init__(self, idx, source="", target="", label="", alphabet_indexes=[]):
        self.idx = idx
        self.source = source
        self.target = target
        self.label = label
        self.alphabet_indexes = alphabet_indexes
    
    def show(self):
        print(self.idx, self.source, self.label, self.target, self.alphabet_indexes)

def rta_to_ra(rta, region_alphabet):
    """Given a realtime automaton, transform it to a region automaton.
    """
    trans = []
    for tran in rta.trans:
        tran_id = tran.id
        label = tran.label
        source = tran.source
        target = tran.target
        alphabet_indexes = []
        for rl, i in zip(region_alphabet[label], range(0, len(region_alphabet[label]))):
            if constraint_subset(rl.region, tran.constraint) == True:
                alphabet_indexes.append(i)
        alphabet_indexes.sort()
        new_tran = RATran(tran_id, source, target, label, alphabet_indexes)
        trans.append(new_tran)
    name = "RA_" + rta.name
    locations = [l for l in rta.locations]
    initstate_names = [init for init in rta.initstate_names]
    accept_names = [accept for accept in rta.accept_names]
    return RegionAutomaton(name, region_alphabet, locations, trans, initstate_names, accept_names)

