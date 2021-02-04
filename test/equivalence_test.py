import unittest
import sys
sys.path.append('../')

from nrta import buildRTA, buildAssistantRTA, build_region_alphabet
from equivalence import equivalence_query



class EquivalenceTest(unittest.TestCase):
    def test_equivalence_query(self):
        A,_ = buildRTA("a.json")
        AA = buildAssistantRTA(A)

        region_alphabet = build_region_alphabet(AA.sigma,AA.max_time_value())

        B,_ = buildRTA("b.json")
        BB = buildAssistantRTA(B)
        equivalent, ctx = equivalence_query(BB, AA, region_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 1})

        C,_ = buildRTA("a.json")
        CC = buildAssistantRTA(C)
        equivalent, ctx = equivalence_query(CC, AA, region_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": True, "value": -2})

        E,_ = buildRTA("empty.json")
        EE = buildAssistantRTA(E)
        equivalent, ctx = equivalence_query(EE, A, region_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 1})

        F,_ = buildRTA("full.json")
        FF = buildAssistantRTA(F)
        equivalent, ctx = equivalence_query(FF, A, region_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": False, "value": 0})

    def test_equivalence_query2(self):
        A,_ = buildRTA("dfa1.json")
        AA = buildAssistantRTA(A)

        region_alphabet = build_region_alphabet(AA.sigma,AA.max_time_value())

        B,_ = buildRTA("dfa2.json")
        BB = buildAssistantRTA(B)
        equivalent, ctx = equivalence_query(BB, AA, region_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": True, "value": -2})
    
    def test_equivalence_query3(self):
        A,_ = buildRTA("dfa1.json")
        AA = buildAssistantRTA(A)

        region_alphabet = build_region_alphabet(AA.sigma,AA.max_time_value())

        B,_ = buildRTA("dfa1.json")
        BB = buildAssistantRTA(B)
        equivalent, ctx = equivalence_query(BB, AA, region_alphabet)
        self.assertEqual({"equivalent": equivalent, "value": ctx.value}, {"equivalent": True, "value": -2})


        

if __name__ == "__main__":
    unittest.main()