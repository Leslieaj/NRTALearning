from fa import FATran, FA
from interval import Constraint
from nrta import Location, RTA, RTATran
#from otatable import *

class EvidenceAutomaton():
    def __init__(self, name,sigma= None, locations=None, trans=None, initstates=None, accept=None):
        self.name = name
        self.sigma = sigma
        self.locations = locations or []
        self.trans = trans or []
        self.initstate_names = initstates or []
        self.accept_names = accept or []
    
    def show(self):
        print("EA name: ")
        print(self.name)
        print("sigma and length of sigma: ")
        print(self.sigma, len(self.sigma))
        print("locations (name, init, accept) :")
        for s in self.locations:
            print(s.name, s.init, s.accept)
        print("transitions (id, source_state, label, target_state): ")
        for t in self.trans:
            print(t.id, t.source, [tw.show() for tw in t.label], t.target)
        print("initial states: ")
        print(self.initstate_names)
        print("accept states: ")
        print(self.accept_names)

class EATran():
    def __init__(self, id, source = "", target = "", label = []):
        self.id = id
        self.source = source
        self.target = target
        self.label = label or []


def table_to_ea(rtatable, n):
    """Given an ota table, build a finite automaton.
    """
    ### First, need to transform the timedwords of the elements in S_U_R 
    ### to clock valuation timedwords with reset informations.
    #S_U_R = [s for s in otatable.S] + [r for r in otatable.R]
    #table_elements = [Element(dRTWs_to_lRTWs(e.tws), e.value) for e in S_U_R]
    table_elements = [s for s in rtatable.S] + [r for r in rtatable.R]
    ### build a finite automaton
    ## FA locations
    rtw_alphabet = []
    locations = []
    initstate_names = []
    accept_names = []
    value_name_dict = {}
    # sink_name = ""
    epsilon_row = None
    for element in table_elements:
        if element.tws == []:
            epsilon_row = element
            break
    prime_rows = rtatable.get_primes()
    #for s,i in zip(rtatable.S, range(1, len(rtatable.S)+1)):
    for s,i in zip(prime_rows, range(1, len(prime_rows)+1)):
        name = str(i)
        value_name_dict[s.whichstate()] = name
        init = False
        accept = False
        if s.is_covered_by(epsilon_row):
            init = True
            initstate_names.append(name)
        if s.value[0] == 1:
            accept = True
            accept_names.append(name)
        # if s.value[0] == -1:
        #     sink_name = name
        temp_state = Location(name, init, accept)
        locations.append(temp_state)
    ## FATrans
    trans_number = 0
    trans = []
    for r in table_elements: # r = ua
        if r.tws == []:
            continue
        timedwords = [tw for tw in r.tws]
        u = timedwords[:-1]
        a = timedwords[len(timedwords)-1]
        if a not in rtw_alphabet:
            rtw_alphabet.append(a)
        source = ""
        # sources = []
        targets = []
        for element in table_elements:
            if u == element.tws and element.whichstate() in value_name_dict:
            #     sources = [value_name_dict[p.whichstate()] for p in prime_rows if p.is_covered_by(element)]
                source = value_name_dict[element.whichstate()]
            if element.is_covered_by(r) and element in prime_rows:
                if value_name_dict[element.whichstate()] not in targets:
                        targets.append(value_name_dict[element.whichstate()])
        # for source in sources:
        if source != "":
            for target in targets:
                need_newtran = True
                for tran in trans:
                    if source == tran.source and target == tran.target:
                        if a.action == tran.label[0].action:
                            need_newtran = False
                            if a not in tran.label:
                                tran.label.append(a)
                            break
                if need_newtran == True:
                    temp_tran = EATran(trans_number, source, target, [a])
                    trans.append(temp_tran)
                    trans_number = trans_number + 1
    ea = EvidenceAutomaton("EA_"+str(n),rtw_alphabet,locations,trans,initstate_names,accept_names)
    return ea

def ea_to_rta(ea, sink_name, sigma, n):
    """Transform the evidence automaton to a real-time automaton as a hypothesis.
    """
    new_name = "H_" + str(n)
    #sigma = [action for action in sigma]
    locations = [Location(l.name,l.init,l.accept) for l in ea.locations]
    initstate_names = [name for name in ea.initstate_names]
    accept_names = [name for name in ea.accept_names]
    # for l in states:
    #     if l.name == sink_name:
    #         l.sink = True
    ### generate the transitions
    trans = []
    for s in ea.locations:
        # for t in ea.locations:
        s_t_dict = {}
        for key in sigma:
            s_t_dict[key] = []
        for tran in ea.trans:
                # if tran.source == s.name and tran.target == t.name:
                    # s_t_dict[tran.label[0].action].extend([rtw.time for rtw in tran.label])
            if tran.source == s.name:
                for rtw in tran.label:
                    if rtw.time not in s_t_dict[tran.label[0].action]:
                        s_t_dict[tran.label[0].action].append(rtw.time)
        for tran in ea.trans:
            # if tran.source == s.name and tran.target == t.name:
            if tran.source == s.name:
                timepoints = [time for time in s_t_dict[tran.label[0].action]]
                timepoints.sort()
                # print(timepoints)
                for rtw in tran.label:
                    index = timepoints.index(rtw.time)
                    temp_constraint = None
                    if index + 1 < len(timepoints):
                        if isinstance(rtw.time,int) and isinstance(timepoints[index+1], int):
                            temp_constraint = Constraint("[" + str(rtw.time) + "," + str(timepoints[index+1]) + ")")
                        elif isinstance(rtw.time,int) and not isinstance(timepoints[index+1], int):
                            temp_constraint = Constraint("[" + str(rtw.time) + "," + str(int(timepoints[index+1])) + "]")
                        elif not isinstance(rtw.time,int) and isinstance(timepoints[index+1], int):
                            temp_constraint = Constraint("(" + str(int(rtw.time)) + "," + str(timepoints[index+1]) + ")")
                        else:
                            temp_constraint = Constraint("(" + str(int(rtw.time)) + "," + str(int(timepoints[index+1])) + "]")
                    else:
                        if isinstance(rtw.time,int):
                            temp_constraint = Constraint("[" + str(rtw.time) + "," + "+" + ")")
                        else:
                            temp_constraint = Constraint("(" + str(int(rtw.time)) + "," + "+" + ")")
                    temp_tran = RTATran(len(trans), tran.source, tran.label[0].action, temp_constraint, tran.target)
                    trans.append(temp_tran)
    rta = RTA(new_name,sigma,locations,trans,initstate_names,accept_names)
    # ota.sink_name = sink_name
    return rta
