# import sys
import json
from interval import Constraint, complement_intervals, min_constraint_number

class Location(object):
    """
        The definition of location.
        "Name" for location name;
        "init" for indicating the initial states;
        "accept" for indicating accepting states;
        "sink" for indicating the location whether it is the sink state.
    """
    def __init__(self, name="", init=False, accept=False, sink=False):
        self.name = name
        self.init = init
        self.accept = accept
        self.sink = sink

    def __eq__(self, location):
        if self.name == location.name and self.init == location.init and self.accept == location.accept:
            return True
        else:
            return False
            
    def __hash__(self):
        return hash(("LOCATION", self.name, self.init, self.accept))

    def get_name(self):
        return self.name

    def show(self):
        return self.get_name() + ',' + str(self.init) + ',' + str(self.accept) + ',' + str(self.sink)


class RTATran(object):
    """
        The definition of RTA transition.
        "source" for the source location name;
        "target" for the target location name;
        "label" for the action name;
        "constraint" for the timing constraints.
    """
    def __init__(self, id, source="", label="", constraint=None, target=""):
        self.id = id
        self.source = source
        self.label = label
        self.constraint = constraint
        self.target = target

    def is_pass(self, tw):
        """Determine whether the timeaction tw can pass the transition.
        """
        if tw.action == self.label and self.constraint.isininterval(tw.time):
            return True
        else:
            return False

    def __eq__(self, rtatran):
        if self.source == rtatran.source and self.label == rtatran.label and self.constraint == rtatran.constraint and self.target == rtatran.target:
            return True
        else:
            return False

    def __hash__(self):
        return hash(("RTATRAN", self.source, self.label, self.constraint, self.target))

    def show_constraint(self):
        """Return a string
        """
        if self.constraint is None:
            return "[0,+)"
        else:
            temp = self.constraint.guard
            return temp

class RTA(object):
    """
        The definition of Real-Timed Automata.
        "name" for the RTA name string;
        "sigma" for the labels list;
        "locations" for the locations list;
        "trans" for the transitions list;
        "initstate_name" for the initial location name;
        "accept_names" fot the list of accepting locations.
    """
    def __init__(self, name, sigma, locations, trans, inits, accepts):
        self.name = name
        self.sigma = sigma or []
        self.locations = locations or []
        self.trans = trans or []
        self.initstate_names = inits or []
        self.accept_names = accepts or []
        self.sink_name = ""
        self.s_a_t = dict()
        for tran in self.trans:
            sa = tran.source + '_' + tran.label
            if sa not in self.s_a_t:
                self.s_a_t[sa] = []
            self.s_a_t[sa].append(tran)
    
    def max_time_value(self):
        """
            Get the max time value constant appearing in RTA.
            Return "max_time_value" for the max time value constant;
        """
        max_time_value = 0
        for tran in self.trans:
            temp_max_value = 0
            if tran.constraint.max_value == '+':
                temp_max_value = int(tran.constraint.min_value)
            else:
                temp_max_value = int(tran.constraint.max_value)
            if max_time_value < temp_max_value:
                max_time_value = temp_max_value
        return max_time_value
    
    def is_accept(self, tws):
        """
            determine whether Nondeterministic-RTA accepts a timed words or not.
        """
        if len(tws) == 0:
            for initstate_name in self.initstate_names:
                if initstate_name in self.accept_names:
                    return 1
            return 0
        else:
            current_statenames = self.initstate_names
            target_statenames = []
            for tw in tws:
                for curr_statename in current_statenames:
                    sa = curr_statename + '_' + tw.action
                    if sa in self.s_a_t:
                        for tran in self.s_a_t[sa]:
                            if tran.is_pass(tw) and tran.target not in target_statenames:
                                target_statenames.append(tran.target)
                current_statenames = [target for target in target_statenames]
                target_statenames = []
                if current_statenames == []:
                    return -2
            for curr_statename in current_statenames:
                if curr_statename in self.accept_names:
                    return 1
            return 0

    def is_accept_rws(self, rws):
        """Given a regionwords, determin whether NRTA accepts the regionwords
        """
        tws = []
        for regionlabel in rws:
            temp_tw_action = regionlabel.label
            temp_tw_time = min_constraint_number(regionlabel.region)
            temp_tws = Timedword(temp_tw_action, temp_tw_time)
            tws.append(temp_tws)
        result = self.is_accept(tws)
        return result

    def show(self):
        print("RTA name: ")
        print(self.name)
        print("sigma and length of sigma: ")
        print(self.sigma, len(self.sigma))
        print("Location (name, init, accept, sink) :")
        for l in self.locations:
            print(l.show())
        print("transitions (id, source_state, label, target_state, constraint): ")
        for t in self.trans:
            print(t.id, t.source, t.label, t.target, t.show_constraint())
            print
        print("init state: ")
        print(self.initstate_names)
        print("accept states: ")
        print(self.accept_names)
        print("sink states: ")
        print(self.sink_name)


class Timedword(object):
    """The definition of timedword.
    """
    def __init__(self, action, time):
        self.action = action
        self.time = time
    
    def __eq__(self, tw):
        if self.action == tw.action and self.time == tw.time:
            return True
        else:
            return False
    
    def __str__(self):
        return self.show()
    
    def __repr__(self):
        return self.show()

    def show(self):
        return '(' + self.action + ',' + str(self.time) + ')'

class Regionlabel(object):
    def __init__(self, index = 0, label="", region = None):
        self.index = index
        self.label = label
        self.region = region
    
    def __eq__(self, rl):
        if self.index == rl.index and self.label == rl.label and self.region == rl.region:
            return True
        else:
            return False
    
    def __hash__(self):
        return hash(("Regionlabel", self.index, self.label, self.region))
    
    def __str__(self):
        return self.show()
    
    def __repr__(self):
        return self.show()
    
    def show_constraints(self):
        return self.region.show()

    def show(self):
        return '(' + str(self.index)  + ',' + self.label + ',' + self.region.show() + ')'

def buildRTA(jsonfile):
    """build the RTA from a json file.
    """
    with open(jsonfile,'r') as f:
        data = json.load(f)
        name = data["name"]
        locations_list = [l for l in data["l"]]
        sigma = [s for s in data["sigma"]]
        trans_set = data["tran"]
        init_list = [l for l in data["init"]]
        accept_list = [l for l in data["accept"]]
        L = [Location(state) for state in locations_list]
        for l in L:
            if l.name in init_list:
                l.init = True
            if l.name in accept_list:
                l.accept = True
        trans = []
        for tran in trans_set:
            tran_id = int(tran)
            source = trans_set[tran][0]
            label = trans_set[tran][1]
            interval_str = trans_set[tran][2]
            new_constraint = Constraint(interval_str.strip())
            target = trans_set[tran][3]
            rta_tran = RTATran(tran_id, source, label, new_constraint, target)
            trans += [rta_tran]
        return RTA(name, sigma, L, trans, init_list, accept_list), sigma

def buildAssistantRTA(rta):
    """Build an assistant RTA which has the partitions at every node.
        The acceptance language is equal to teacher.
    """
    location_number = len(rta.locations)
    tran_number = len(rta.trans)
    new_location = Location(str(location_number+1), False, False)
    new_trans = []
    for l in rta.locations:
        l_dict = {}
        for key in rta.sigma:
            l_dict[key] = []
        for tran in rta.trans:
            if tran.source == l.name:
                for label in rta.sigma:
                    if tran.label == label:
                        if tran.constraint not in l_dict[label]:
                            l_dict[label].append(tran.constraint)
        for key in l_dict:
            cuintervals = []
            if len(l_dict[key]) > 0:
                cuintervals = complement_intervals(l_dict[key])
            else:
                cuintervals = [Constraint("[0,+)")]
            if len(cuintervals) > 0:
                for c in cuintervals:
                    temp_tran = RTATran(tran_number, l.name, key, c, new_location.name)
                    tran_number = tran_number+1
                    new_trans.append(temp_tran)
    assist_name = "Assist_"+rta.name
    assist_locations = [location for location in rta.locations]
    assist_trans = [tran for tran in rta.trans]
    assist_inits = [sn for sn in rta.initstate_names]
    assist_accepts = [sn for sn in rta.accept_names]
    if len(new_trans) > 0:
        assist_locations.append(new_location)
        for tran in new_trans:
            assist_trans.append(tran)
        for label in rta.sigma:
            tmp_constraint = Constraint("[0,+)")
            temp_tran = RTATran(tran_number, new_location.name, label, tmp_constraint, new_location.name)
            tran_number = tran_number+1
            assist_trans.append(temp_tran)
    assist_ota = RTA(assist_name, rta.sigma, assist_locations, assist_trans, assist_inits, assist_accepts)
    assist_ota.sink_name = new_location.name
    return assist_ota

def build_region_alphabet(sigma, max_time_value):
    """Return region alphabet. A region alphabet is a dict. {a: [a1,a2,...,am], b: [b1,b2,...,bn], ...}, ai and bj are regionlabels.
       The index of the regionlabel is starting from 0 for each untime action. Then at every integer point region, the index is equal to 2*integer.
    """
    region_alphabet = {}
    for action in sigma:
        regions = []
        index = 0  
        for i in range(max_time_value+1):
            point_region = Regionlabel(index, action, Constraint("[" + str(i) + "," + str(i) + "]"))
            regions.append(point_region)
            index = index + 1
            if i != max_time_value:
                interval_region = Regionlabel(index, action, Constraint("(" + str(i) + "," + str(i+1) + ")")) 
                regions.append(interval_region)
                index = index + 1
            else:
                interval_region = Regionlabel(index, action, Constraint("(" + str(i) + "," + "+" + ")")) 
                regions.append(interval_region)
                index = index + 1
        region_alphabet[action] = regions
    return region_alphabet
        

# def main():
#     print("------------------A-----------------")
#     paras = sys.argv
#     A,_ = buildRTA(paras[1])
#     A.show()
#     print("------------------Assist-----------------")
#     AA = buildAssistantRTA(A)
#     AA.show()
#     print("--------------max value---------------------")
#     print(AA.max_time_value())

# if __name__=='__main__':
# 	main()