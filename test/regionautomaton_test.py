import unittest
import sys
sys.path.append('../')

from interval import Constraint
from nrta import buildRTA, buildAssistantRTA, build_region_alphabet
from regionautomaton import rta_to_ra, nfa_to_dfa, ra_to_rta, completed_dfa_complement

A, _ = buildRTA('a.json')
AA = buildAssistantRTA(A)  # Assist

class EquivalenceTest(unittest.TestCase):   
    def test_rta_to_fa_2(self):
        max_time_value = AA.max_time_value()
        region_alphabet = build_region_alphabet(AA.sigma,max_time_value)
        AA_FA = rta_to_ra(AA,region_alphabet)
        # AA_FA.show()

    def test_nfa_to_dfa(self):
        max_time_value = AA.max_time_value()
        region_alphabet = build_region_alphabet(AA.sigma,max_time_value)
        AA_RA = rta_to_ra(AA,region_alphabet)
        AA_RA_D = nfa_to_dfa(AA_RA)
        # AA_RA_D.show()
    
    def test_completed_dfa_complement(self):
        max_time_value = AA.max_time_value()
        region_alphabet = build_region_alphabet(AA.sigma,max_time_value)
        AA_RA = rta_to_ra(AA,region_alphabet)
        AA_RA_D = nfa_to_dfa(AA_RA)
        C_AA_RA_D = completed_dfa_complement(AA_RA_D)
        
        ln1 = [l.name for l in AA_RA_D.locations]
        ln2 = [l.name for l in C_AA_RA_D.locations]
        accept = [item for item in ln1 if item not in C_AA_RA_D.accept_names]
        accept.sort()
        self.assertEqual(len(AA_RA_D.locations), len(C_AA_RA_D.locations))
        self.assertEqual(ln1, ln2)
        self.assertEqual(C_AA_RA_D.initstate_names, AA_RA_D.initstate_names)
        self.assertEqual(accept, AA_RA_D.accept_names)
    
    def test_ra_to_rta(self):
        max_time_value = AA.max_time_value()
        region_alphabet = build_region_alphabet(AA.sigma,max_time_value)
        AA_RA = rta_to_ra(AA,region_alphabet)
        AA_RA_D = nfa_to_dfa(AA_RA)
        AA_DRTA = ra_to_rta(AA_RA_D)
        AA_DRTA.show()


if __name__ == "__main__":
    unittest.main()