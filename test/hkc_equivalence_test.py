import unittest
import sys
sys.path.append('../')
from hkc_equivalence import *


class HKCEquivalenceTest(unittest.TestCase):
    def test_equivalence_query(self):
        A,_ = buildRTA("test/a.json")
        AA = buildAssistantRTA(A)

        temp_alphabet = []
        for tran in AA.trans:
            label = tran.label
            constraint = tran.constraint
            timed_label = Timedlabel("",label,[constraint])
            if timed_label not in temp_alphabet:
                temp_alphabet += [timed_label]
        teacher_timed_alphabet = alphabet_classify(temp_alphabet, AA.sigma)

        B,_ = buildRTA("test/b.json")
        BB = buildAssistantRTA(B)
        equivalent, ctx = equivalence_query(BB, AA, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 1})

        C,_ = buildRTA("test/a.json")
        CC = buildAssistantRTA(C)
        equivalent, ctx = equivalence_query(CC, AA, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": True, "value": -2})

        E,_ = buildRTA("test/empty.json")
        EE = buildAssistantRTA(E)
        equivalent, ctx = equivalence_query(EE, AA, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 1})

        F,_ = buildRTA("test/full.json")
        FF = buildAssistantRTA(F)
        equivalent, ctx = equivalence_query(FF, AA, teacher_timed_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 0})


if __name__ == "__main__":
    unittest.main()
