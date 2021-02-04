# Definition of the region automaton
import copy
from interval import constraint_subset, unintersect_intervals
from nrta import Location, RTA, RTATran

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

def nfa_to_dfa(rfa):
    """Convert Nondeterministic FA (region automaton) to Deterministic FA (region automaton).
    The input 'rfa' is a region automaton..
    """
    name = rfa.name
    timed_alphabet = rfa.region_alphabet
    # for locations
    newstate_list = []
    rfa.initstate_names.sort()
    newstate_list.append(rfa.initstate_names)
    final_newstate = copy.deepcopy(newstate_list)
    f = {}
    statename_value = {}
    index = 0
    while len(newstate_list) > 0:
        temp_state = newstate_list.pop(0)
        index = index + 1
        state_name = str(index)
        statename_value[state_name] = temp_state
        f[state_name] = {}
        for term in timed_alphabet:
            for nf in timed_alphabet[term]:
                i = timed_alphabet[term].index(nf)
                f[state_name][term+'_'+str(i)] = []
                label_targetlist = []
                for tran in rfa.trans:
                    if tran.source in temp_state and term == tran.label and i in tran.alphabet_indexes:
                        if tran.target not in label_targetlist:
                            label_targetlist.append(tran.target)
                            label_targetlist.sort()
                f[state_name][term+'_'+str(i)].extend(label_targetlist)
                if label_targetlist not in final_newstate:
                    if len(label_targetlist) > 0:
                        newstate_list.append(label_targetlist)
                        final_newstate.append(label_targetlist)
    locations = []
    initstate_names = []
    accept_names = []
    for statename in f:
        init = False
        accept = False
        statename_value[statename].sort()
        rfa.initstate_names.sort()
        if statename_value[statename] == rfa.initstate_names:
            init = True
        for sn in statename_value[statename]:
            # if sn == rfa.initstate_name and len(statename_value[statename]) == 1:
            #     init = True
            if sn in rfa.accept_names:
                accept = True
        new_location = Location(statename, init, accept)
        locations.append(new_location)
        if init == True:
            initstate_names.append(statename)
        if accept == True:
            accept_names.append(statename)
    initstate_names.sort()
    accept_names.sort()

    refined_f = copy.deepcopy(f)
    for statename in refined_f:
        for label in refined_f[statename]:
            for key in statename_value:
                if refined_f[statename][label] == statename_value[key]:
                    refined_f[statename][label] = key
    # for transitions
    trans = []
    for statename in refined_f:
        source = statename
        target_label = {}
        for label in refined_f[statename]:
            if len(refined_f[statename][label]) > 0:
                new_target = refined_f[statename][label]
                if new_target not in target_label:
                    target_label[new_target] = []
                    target_label[new_target].append(label)
                else:
                    target_label[new_target].append(label)
        for target in target_label:
            labels = target_label[target]
            label_nfnums = {}
            for label_nfnum in labels:
                label, nfnum = label_nfnum.split('_')
                if label not in label_nfnums:
                    label_nfnums[label] = []
                    label_nfnums[label].append(int(nfnum))
                else:
                    label_nfnums[label].append(int(nfnum))
            for label in label_nfnums:
                nfnums = label_nfnums[label]
                nfnums.sort()
                if len(nfnums) > 0:
                    new_tran = RATran(len(trans), source, target, label, nfnums)
                    trans.append(new_tran)

    d_rfa = RegionAutomaton(name, timed_alphabet, locations, trans, initstate_names, accept_names)
    return d_rfa

def completed_dfa_complement(dfa):
    """dfa: the input is a DFA (deterministic region automaton). 
    So the complement operation just changes the acceptence of the locations
    """
    name = "C_" + dfa.name
    locations = copy.deepcopy(dfa.locations)
    # timed_alphabet = copy.deepcopy(dfa.timed_alphabet)
    trans = copy.deepcopy(dfa.trans)
    # initstate_name = dfa.initstate_name
    accept_names = []
    for s in locations:
        if s.accept == True:
            s.accept = False
        else:
            s.accept = True
            accept_names.append(s.name)
    comp_rfa = RegionAutomaton(name, dfa.region_alphabet, locations, trans, dfa.initstate_names, accept_names)
    return comp_rfa

def rfa_product(rfa1, rfa2):
    """Given two DFA (region automata), return their product DFA
    """
    name = 'P_'+rfa1.name+'_'+rfa2.name
    timed_alphabet = rfa1.region_alphabet # has same timed alphabet
    reach_states = []
    temp_states = []
    final_states = []
    for state1 in rfa1.locations:
        for state2 in rfa2.locations:
            new_state_name = state1.name + '_' + state2.name
            new_state_init = False
            new_state_accept = False
            if state1.init == True and state2.init == True:
                new_state_init = True
            if state1.accept == True and state2.accept == True:
                new_state_accept = True
            new_state = Location(new_state_name, new_state_init, new_state_accept)
            temp_states.append(new_state)
            if new_state_init == True:
                reach_states.append(new_state)
                final_states.append(new_state)
    trans = []
    #final_states = []
    while len(reach_states) > 0:
        rstate = reach_states.pop(0)
        statename1, statename2 = rstate.name.split('_')
        for tran1 in rfa1.trans:
            if tran1.source == statename1:
                target1 = tran1.target
                label1 = tran1.label
                nfnums1 = tran1.alphabet_indexes
                for tran2 in rfa2.trans:
                    if tran2.source == statename2:
                        target2 = tran2.target
                        label2 = tran2.label
                        nfnums2 = tran2.alphabet_indexes
                        new_nfnums = []
                        if label1 == label2:
                            new_label = label1
                            for i in nfnums1:
                                for j in nfnums2:
                                    if i == j:
                                        new_nfnums.append(i)
                            new_target = target1 + '_' + target2
                            if len(new_nfnums) > 0:
                                new_tran = RATran(len(trans), rstate.name, new_target, new_label, new_nfnums)
                                trans.append(new_tran)
                                for state in temp_states:
                                    if state.name == new_target:
                                        if state not in final_states:
                                            reach_states.append(state)
                                            final_states.append(state)
        #final_states.append(rstate)
    initstate_names = []
    accept_names = []
    for state in final_states:
        if state.init == True:
            initstate_names.append(state.name)
        if state.accept == True:
            accept_names.append(state.name)
    product_rfa = RegionAutomaton(name, timed_alphabet, final_states, trans, initstate_names, accept_names)
    return product_rfa

def ra_to_rta(rfa, n=0):
    """Given a region automaton rfa, convert it to a RTA.
       "n": hypothesis index. '0' represents the teacher
    """
    name = "Teacher"
    if n != 0:
        name = "HA" + str(n)
    locations = copy.deepcopy(rfa.locations)
    sigma = [term for term in rfa.region_alphabet]
    trans = []
    for tran in rfa.trans:
        source = tran.source
        target = tran.target
        label = tran.label
        temp_constraints = [rfa.region_alphabet[label][i].region for i in tran.alphabet_indexes]
        constraints = unintersect_intervals(temp_constraints)
        for constraint in constraints:
            new_tran = RTATran(len(trans), source, label, constraint, target)
            trans.append(new_tran)
    initstate_name = copy.deepcopy(rfa.initstate_names)
    accept_names = copy.deepcopy(rfa.accept_names)
    rta = RTA(name, sigma, locations, trans, initstate_name, accept_names)
    return rta