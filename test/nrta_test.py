import unittest
import sys
sys.path.append('../')

from nrta import *

A, _ = buildRTA('a.json')
AA = buildAssistantRTA(A)  # Assist

tws0 = []
tws1 = [Timedword('a',1), Timedword('b',1)]
tws2 = [Timedword('a',2), Timedword('a',6)]
tws3 = [Timedword('a',2), Timedword('a',4)]
tws4 = [Timedword('a',2.5), Timedword('b',6)]
tws5 = [Timedword('a',2.5), Timedword('b',0)]
tws6 = [Timedword('a',2.5), Timedword('b',1.5), Timedword('a',2.1), Timedword('b',3.5)]
tws7 = [Timedword('a',2.5), Timedword('b',1.5), Timedword('a',2.1), Timedword('b',3)]
tws8 = [Timedword('a',2.5), Timedword('b',1.5), Timedword('a',2.1), Timedword('b',3.5), Timedword('a',2)]
tws9 = [Timedword('a',2.5), Timedword('b',1.5), Timedword('a',2.1), Timedword('b',3.5), Timedword('a',2), Timedword('b',3.5)]

class EquivalenceTest(unittest.TestCase):
    def test_max_time_value(self):
        self.assertEqual(AA.max_time_value(), 9)
    
    def test_is_accept(self):
        self.assertEqual(AA.is_accept(tws0), False)
        self.assertEqual(AA.is_accept(tws1), False)
        self.assertEqual(AA.is_accept(tws2), True)
        self.assertEqual(AA.is_accept(tws3), False)
        self.assertEqual(AA.is_accept(tws4), True)
        self.assertEqual(AA.is_accept(tws5), False)
        self.assertEqual(AA.is_accept(tws6), True)
        self.assertEqual(AA.is_accept(tws7), False)
        self.assertEqual(AA.is_accept(tws8), False)
        self.assertEqual(AA.is_accept(tws9), True)
        
if __name__ == "__main__":
    unittest.main()