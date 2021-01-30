import unittest
import sys
sys.path.append('../')

from interval import Constraint
from nrta import buildRTA, buildAssistantRTA, build_region_alphabet
from regionautomaton import rta_to_ra
from fa import Timedlabel, alphabet_classify, alphabet_partitions, rta_to_fa

A, _ = buildRTA('a.json')
AA = buildAssistantRTA(A)  # Assist

class EquivalenceTest(unittest.TestCase):   
    def test_rta_to_fa_2(self):
        max_time_value = AA.max_time_value()
        region_alphabet = build_region_alphabet(AA.sigma,max_time_value)
        AA_FA = rta_to_ra(AA,region_alphabet)
        AA_FA.show()


if __name__ == "__main__":
    unittest.main()