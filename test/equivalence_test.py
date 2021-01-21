import unittest
import sys
sys.path.append('../')
from equivalence import *



class EquivalenceTest(unittest.TestCase):
    def test_equivalence_query(self):
        A,_ = buildRTA("a.json")
        #AA = buildAssistantRTA(A)

        temp_alphabet = []
        for tran in A.trans:
            label = tran.label
            constraint = tran.constraint
            timed_label = Timedlabel("",label,[constraint])
            if timed_label not in temp_alphabet:
                temp_alphabet += [timed_label]
        teacher_timed_alphabet = alphabet_classify(temp_alphabet, A.sigma)

        B,_ = buildRTA("b.json")
        BB = buildAssistantRTA(B)
        equivalent, ctx = equivalence_query(BB, A, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 1})

        C,_ = buildRTA("a.json")
        CC = buildAssistantRTA(C)
        equivalent, ctx = equivalence_query(CC, A, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": True, "value": -2})

        E,_ = buildRTA("empty.json")
        EE = buildAssistantRTA(E)
        equivalent, ctx = equivalence_query(EE, A, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 1})

        F,_ = buildRTA("full.json")
        FF = buildAssistantRTA(F)
        equivalent, ctx = equivalence_query(FF, A, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 0})

    def test_equivalence_query2(self):
        A,_ = buildRTA("dfa1.json")
        #AA = buildAssistantRTA(A)

        temp_alphabet = []
        for tran in A.trans:
            label = tran.label
            constraint = tran.constraint
            timed_label = Timedlabel("",label,[constraint])
            if timed_label not in temp_alphabet:
                temp_alphabet += [timed_label]
        teacher_timed_alphabet = alphabet_classify(temp_alphabet, A.sigma)

        B,_ = buildRTA("dfa2.json")
        BB = buildAssistantRTA(B)
        equivalent, ctx = equivalence_query(BB, A, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": True, "value": -2})


        

if __name__ == "__main__":
    unittest.main()