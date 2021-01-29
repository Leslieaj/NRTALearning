import unittest
import sys
sys.path.append('../')

from interval import Constraint
from nrta import buildRTA, buildAssistantRTA, build_region_alphabet
from fa import Timedlabel, alphabet_classify, alphabet_partitions, rta_to_fa

A, _ = buildRTA('a.json')
AA = buildAssistantRTA(A)  # Assist

temp_alphabet = []
for tran in AA.trans:
    label = tran.label
    constraint = tran.constraint
    timed_label = Timedlabel("",label,[constraint])
    if timed_label not in temp_alphabet:
        temp_alphabet += [timed_label]
timed_alphabet = alphabet_classify(temp_alphabet, AA.sigma)

class EquivalenceTest(unittest.TestCase):
    def test_alphabet_partitions(self):
        partitioned_alphabet, bnlist_dict = alphabet_partitions(timed_alphabet)
        alphabet_dict = {}
        alphabet_dict['a'] = [Timedlabel("a_0","a",[Constraint("[0,1)")]), 
                              Timedlabel("a_1","a",[Constraint("[1,2)")]), 
                              Timedlabel("a_2","a",[Constraint("[2,2]")]), 
                              Timedlabel("a_3","a",[Constraint("(2,3)")]), 
                              Timedlabel("a_4","a",[Constraint("[3,5)")]), 
                              Timedlabel("a_5","a",[Constraint("[5,+)")])]
        alphabet_dict['b'] = [Timedlabel("b_0","b",[Constraint("[0,1]")]), 
                              Timedlabel("b_1","b",[Constraint("(1,3]")]),
                              Timedlabel("b_2","b",[Constraint("(3,4)")]), 
                              Timedlabel("b_3","b",[Constraint("[4,9]")]),
                              Timedlabel("b_4","b",[Constraint("(9,+)")])]
        self.assertEqual(partitioned_alphabet, alphabet_dict)

    def test_rta_to_fa(self):
        partitioned_alphabet, bnlist_dict = alphabet_partitions(timed_alphabet)
        AA_FA = rta_to_fa(AA,partitioned_alphabet)
        for tran in AA_FA.trans:
            if tran.id == 3:
                self.assertEqual({"source": tran.source, "target": tran.target, "timedlabel":tran.aphabet_indexes},
                {"source": "2", "target": "3", "timedlabel":[2, 3]})
    
    def test_rta_to_fa_2(self):
        max_time_value = AA.max_time_value()
        region_alphabet = build_region_alphabet(AA.sigma,max_time_value)
        AA_FA = rta_to_fa(AA,region_alphabet)
        AA_FA.show()


if __name__ == "__main__":
    unittest.main()