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
        print("transitions: (id, source, label, target, timedlabel, index): ")
        for t in self.trans:
            #print(t.id, t.source, t.label, t.timedlabel.show_constraints(), t.target)
            print(t.id, t.source, t.label, t.target, t.timedlabel.show_constraints(), [t.timedlabel.label + "_" + str(num) for num in t.nfnums])
        print("init state: ")
        print(self.initstate_name)
        print("accept states: ")
        print(self.accept_names)

class FATran:
    def __init__(self, id, source="", target="", label="", timedlabel=None, nfnums=[]):
        self.id = id
        self.source = source
        self.target = target
        self.label = label
        self.timedlabel = timedlabel
        self.nfnums = nfnums

    def show(self):
        print(self.id, self.source, self.label, self.target, self.timedlabel.show(), self.nfnums)


def rta_to_fa(rta, alphabet_partitions):
    timed_alphabet = copy.deepcopy(alphabet_partitions)
    trans = []
    for tran in rta.trans:
        tran_id = tran.id
        label = tran.label
        source = tran.source
        target = tran.target
        temp_partitions = []
        nfnums = []
        for tl, i in zip(timed_alphabet[label], range(0, len(timed_alphabet[label]))):
            if constraint_subset(tl.constraints[0], tran.constraint) == True:
                nfnums.append(i)
                temp_partitions.append(tl.constraints[0])
        #print(nfnums)
        new_tran = FATran(tran_id, source, target, label, Timedlabel("",label,temp_partitions), nfnums)
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


def main():
    print("---------------------a.json----------------")
    paras = sys.argv
    A,_ = buildRTA(paras[1], 's')
    print("------------------Assist-----------------")
    AA = buildAssistantRTA(A, 's')
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
    print("------------------------------------------")
    partitioned_alphabet, bnlist_dict = alphabet_partitions(AA_FA.timed_alphabet)
    for key in partitioned_alphabet:
        print(key)
        for c in partitioned_alphabet[key]:
            print(c.show())

if __name__=='__main__':
	main()