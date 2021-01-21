from interval import *
from nrta import *

class Timedlabel(object):
    def __init__(self, name="", label="", constraints=[]):
        self.name = name
        self.label = label
        self.constraints = constraints
        lbsort(self.constraints)
    
    def __eq__(self, timedlabel):
        if self.label == timedlabel.label and len(self.constraints) == len(timedlabel.constraints):
            templist = [c for c in self.constraints if c in timedlabel.constraints]
            if len(templist) == len(self.constraints):
                return True
            else:
                return False
        else:
            return False
    
    def __str__(self):
        return self.show()
        
    def __repr__(self):
        return self.show()

    def show_constraints(self):
        s = ""
        for c in self.constraints[:-1]:
            s = s + c.show() + 'U'
        s = s + self.constraints[len(self.constraints)-1].show()
        return s

    def show(self):
        return "(" + self.name + "," + self.label+ "," + self.show_constraints() + ")"


class FA(object):
    """The definition of finite automaton.
    "name" for the FA name string;
    "timed_alphabet" for a dict of timedlabel, e.g. {"a": ("a1", "a", [(0,1), [2,4)])}
    "locations" for the locations list;
    "trans" for the transitions list;
    "initstate_name" for the initial location name;
    "accept_names" fot the list of accepting locations.
    """
    def __init__(self, name="", timed_alphabet = {}, locations = [], trans = [], initstate_name = "", accept_names = []):
        self.name = name
        self.timed_alphabet = timed_alphabet
        self.locations = locations
        self.trans = trans
        self.initstate_name = initstate_name
        self.accept_names = accept_names
    
    def find_location_by_name(self, lname):
        for l in self.locations:
            if l.name == lname:
                return l
        return None
    
    def show(self):
        print("FA name: ")
        print(self.name)
        print("timed alphabet: ")
        for term in self.timed_alphabet:
            print(term)
            print([timedlabel.show_constraints() for timedlabel in self.timed_alphabet[term]])
        print("Location (name, init, accept, sink)")
        for l in self.locations:
            print(l.name, l.init, l.accept, l.sink)
        print("transitions: (id, source, label, target, timedlabel, symbolic_action): ")
        for t in self.trans:
            constraints = []
            for num in t.aphabet_indexes:
                constraints.append(self.timed_alphabet[t.label][num].constraints[0])
            print(t.id, t.source, t.label, t.target, constraints, [t.label + "_" + str(num) for num in t.aphabet_indexes])
        print("init state: ")
        print(self.initstate_name)
        print("accept states: ")
        print(self.accept_names)

class FATran:
    def __init__(self, id, source="", target="", label="", aphabet_indexes=[]):
        self.id = id
        self.source = source
        self.target = target
        self.label = label
        #self.timedlabel = timedlabel
        self.aphabet_indexes = aphabet_indexes

    def show(self):
        print(self.id, self.source, self.label, self.target, self.aphabet_indexes)


def rta_to_fa(rta, alphabet_partitions):
    timed_alphabet = copy.deepcopy(alphabet_partitions)
    trans = []
    for tran in rta.trans:
        tran_id = tran.id
        label = tran.label
        source = tran.source
        target = tran.target
        aphabet_indexes = []
        for tl, i in zip(timed_alphabet[label], range(0, len(timed_alphabet[label]))):
            if constraint_subset(tl.constraints[0], tran.constraint) == True:
                aphabet_indexes.append(i)
        aphabet_indexes.sort()
        new_tran = FATran(tran_id, source, target, label, aphabet_indexes)
        trans.append(new_tran)
    name = "FA_" + rta.name
    locations = [l for l in rta.locations]
    initstate_name = rta.initstate_name
    accept_names = [accept for accept in rta.accept_names]
    return FA(name, timed_alphabet, locations, trans, initstate_name, accept_names)

def alphabet_classify(timed_alphabet, sigma):
    temp_set = {}
    for label in sigma:
        temp_set[label] = []
        for timedlabel in timed_alphabet:
            if timedlabel.label == label and timedlabel not in temp_set[label]:
                temp_set[label].append(timedlabel)
    return temp_set

def alphabet_combine(alphabet1, alphabet2):
    combined_alphabet = {}
    for key in alphabet1:
        combined_alphabet[key] = []
        for temp1 in alphabet1[key]:
            if temp1 not in combined_alphabet[key]:
                combined_alphabet[key].append(temp1)
        for temp2 in alphabet2[key]:
            if temp2 not in combined_alphabet[key]:
                combined_alphabet[key].append(temp2)
    return combined_alphabet

def alphabet_partitions(classified_alphabet):
    floor_bn = BracketNum('0',Bracket.LC)
    ceil_bn = BracketNum('+',Bracket.RO)
    partitioned_alphabet = {}
    bnlist_dict = {}
    for key in classified_alphabet:
        partitioned_alphabet[key] = []
        timedlabel_list = classified_alphabet[key]
        key_bns = []
        key_bnsc = []
        for timedlabel in timedlabel_list:
            temp_constraints = timedlabel.constraints
            for constraint in temp_constraints:
                min_bn = None
                max_bn = None
                temp_min = constraint.min_value
                temp_minb = None
                if constraint.closed_min == True:
                    temp_minb = Bracket.LC
                else:
                    temp_minb = Bracket.LO
                temp_max = constraint.max_value
                temp_maxb = None
                if constraint.closed_max == True:
                    temp_maxb = Bracket.RC
                else:
                    temp_maxb = Bracket.RO
                min_bn = BracketNum(temp_min, temp_minb)
                max_bn = BracketNum(temp_max, temp_maxb)
                if min_bn not in key_bns:
                    key_bns+= [min_bn]
                if max_bn not in key_bns:
                    key_bns+=[max_bn]
        key_bnsc = copy.deepcopy(key_bns)
        for bn in key_bns:
            bnc = bn.complement()
            if bnc not in key_bnsc:
                key_bnsc.append(bnc)
        if floor_bn not in key_bnsc:
            key_bnsc.append(floor_bn)
        if ceil_bn not in key_bnsc:
            key_bnsc.append(ceil_bn)
        key_bnsc.sort()
        bnlist_dict[key] = key_bnsc
        for index in range(len(key_bnsc)):
            if index%2 == 0:
                temp_constraint = Constraint(key_bnsc[index].getbn()+','+key_bnsc[index+1].getbn())
                temp_timedlabel = Timedlabel("",key, [temp_constraint])
                partitioned_alphabet[key].append(temp_timedlabel)
    for term in partitioned_alphabet:
        for timedlabel,index in zip(partitioned_alphabet[term], range(len(partitioned_alphabet[term]))):
            timedlabel.name = term + '_'+ str(index)
    return partitioned_alphabet, bnlist_dict

def nfa_to_dfa(rfa):
    """Convert Nondeterministic FA to Deterministic FA.
    The input 'rfa' is an FA which is transformed from a RTA.
    """
    name = rfa.name
    timed_alphabet = copy.deepcopy(rfa.timed_alphabet)
    # for locations
    newstate_list = []
    newstate_list.append([rfa.initstate_name])
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
                    if tran.source in temp_state and term == tran.label and i in tran.aphabet_indexes:
                        if tran.target not in label_targetlist:
                            label_targetlist.append(tran.target)
                f[state_name][term+'_'+str(i)].extend(label_targetlist)
                if label_targetlist not in final_newstate:
                    if len(label_targetlist) > 0:
                        newstate_list.append(label_targetlist)
                        final_newstate.append(label_targetlist)
    locations = []
    initstate_name = ""
    accept_names = []
    for statename in f:
        init = False
        accept = False
        for sn in statename_value[statename]:
            if sn == rfa.initstate_name and len(statename_value[statename]) == 1:
                init = True
            if sn in rfa.accept_names:
                accept = True
        new_location = Location(statename, init, accept)
        locations.append(new_location)
        if init == True:
            initstate_name = statename
        if accept == True:
            accept_names.append(statename)

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
                    new_tran = FATran(len(trans), source, target, label, nfnums)
                    trans.append(new_tran)

    d_rfa = FA(name, timed_alphabet, locations, trans, initstate_name, accept_names)
    return d_rfa

def completed_dfa_complement(dfa):
    """dfa: the input is a DFA. 
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
    comp_rfa = FA(name, dfa.timed_alphabet, locations, trans, dfa.initstate_name, accept_names)
    return comp_rfa

def rfa_product(rfa1, rfa2):
    """Given two DFA, return their product DFA
    """
    name = 'P_'+rfa1.name+'_'+rfa2.name
    timed_alphabet = rfa1.timed_alphabet # has same timed alphabet
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
                nfnums1 = tran1.aphabet_indexes
                for tran2 in rfa2.trans:
                    if tran2.source == statename2:
                        target2 = tran2.target
                        label2 = tran2.label
                        nfnums2 = tran2.aphabet_indexes
                        new_nfnums = []
                        if label1 == label2:
                            new_label = label1
                            for i in nfnums1:
                                for j in nfnums2:
                                    if i == j:
                                        new_nfnums.append(i)
                            new_target = target1 + '_' + target2
                            if len(new_nfnums) > 0:
                                new_tran = FATran(len(trans), rstate.name, new_target, new_label, new_nfnums)
                                trans.append(new_tran)
                                for state in temp_states:
                                    if state.name == new_target:
                                        if state not in final_states:
                                            reach_states.append(state)
                                            final_states.append(state)
        #final_states.append(rstate)
    initstate_name = ""
    accept_names = []
    for state in final_states:
        if state.init == True:
            initstate_name = state.name
        if state.accept == True:
            accept_names.append(state.name)
    product_rfa = FA(name, timed_alphabet, final_states, trans, initstate_name, accept_names)
    return product_rfa

def fa_to_rta(rfa):
    """Given a FA rfa, convert it to a RTA.
    """
    name = rfa.name
    locations = copy.deepcopy(rfa.locations)
    sigma = [term for term in rfa.timed_alphabet]
    trans = []
    for tran in rfa.trans:
        tran_id = tran.id
        source = tran.source
        target = tran.target
        label = tran.label
        temp_constraints = [rfa.timed_alphabet[label][i].constraints[0] for i in tran.aphabet_indexes]
        constraints = unintersect_intervals(temp_constraints)
        for constraint in constraints:
            new_tran = RTATran(tran_id, source, label, constraint, target)
            trans.append(new_tran)
    initstate_name = rfa.initstate_name
    accept_names = copy.deepcopy(rfa.accept_names)
    rta = RTA(name, sigma, locations, trans, initstate_name, accept_names)
    return rta

def main():
    print("---------------------a.json----------------")
    paras = sys.argv
    A,_ = buildRTA(paras[1])
    print("------------------Assist-----------------")
    AA = buildAssistantRTA(A)
    print("-----------AA to FA-----------------------")
    temp_alphabet = []
    for tran in AA.trans:
        label = tran.label
        constraint = tran.constraint
        timed_label = Timedlabel("",label,[constraint])
        if timed_label not in temp_alphabet:
            temp_alphabet += [timed_label]
    timed_alphabet = alphabet_classify(temp_alphabet, AA.sigma)
    partitioned_alphabet, bnlist_dict = alphabet_partitions(timed_alphabet)
    AA_FA = rta_to_fa(AA,partitioned_alphabet)
    AA_FA.show()
    # print("------------------------------------------")
    # partitioned_alphabet, bnlist_dict = alphabet_partitions(AA_FA.timed_alphabet)
    # for key in partitioned_alphabet:
    #     print(key)
    #     for c in partitioned_alphabet[key]:
    #         print(c.show())
    print("-------------nfa_to_dfa-----------------------------")
    AA_DFA = nfa_to_dfa(AA_FA)
    AA_DFA.show()
    print("-------------fa_to_rta------------------------------")
    AA_DFA_rta = fa_to_rta(AA_DFA)
    AA_DFA_rta.show()
    # print("-------------completed_dfa_complement--------------")
    # C_AA_DFA = completed_dfa_complement(AA_DFA)
    # C_AA_DFA.show()
    # print("---------------B--------------------------------")
    # B,_ = buildRTA(paras[1])
    # B.show()
    # print("---------------B_DFA--------------------------------")
    # B_FA = rta_to_fa(B,partitioned_alphabet)
    # B_DFA = nfa_to_dfa(B_FA)
    # B_DFA.show()
    # print("-----------------------fa_to_rta----------------------------")
    # B_rta = fa_to_rta(B_DFA)
    # B_rta.show()


if __name__=='__main__':
	main()