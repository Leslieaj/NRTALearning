import unittest
import sys
sys.path.append('../')

from nrta import Timedword
from observation import *

tw1 = Timedword("a", 0)
tw2 = Timedword("b", 0)
tw3 = Timedword("a", 5)
tw4 = Timedword("b", 4)
tw5 = Timedword("a", 7)
tw6 = Timedword("b", 2)
tws0 = []  # empty
tws1 = [tw1]  # (a,0)
tws2 = [tw2]  # (b,0)
tws3 = [tw3]  # (a,5)
tws4 = [tw3, tw1]  # (a,5) (a,0)
tws5 = [tw3, tw2]  # (a,5) (b,0)
tws6 = [tw5]  # (a,7)
tws7 = [tw4]  # (b,4)
tws8 = [tw4, tw3]  # (b,4) (a,5)
tws9 = [tw1, tw1]  # (a,0) (a,0)
tws10 = [tw1, tw2]  # (a,0) (b,0)
tws11 = [tw6, tw3]  # (b,2) (a,5)
tws12 = [tw6]  # (b,2)

e0 = Element(tws0, [0])
e1 = Element(tws1, [0])
e2 = Element(tws2, [0])
e3 = Element(tws3, [1])
e4 = Element(tws4, [0, 1, 0, 1])
e5 = Element(tws5, [1, 1, 0, 1])
e6 = Element(tws5, [1, 0, 0, 1])
e7 = Element(tws5, [1, 0, 0, 0])
e8 = Element(tws5, [0, 0, 0, 0])
e9 = Element(tws5, [1, 1, 1, 1])
e10 = Element(tws5, [0, 0, 1, 0])
e11 = Element(tws5, [1, 0, 1, 0])

e12 = Element(tws5, [0, 1, 0, 0])
e13 = Element(tws5, [0, 1, 1, 0])
e14 = Element(tws5, [0, 1, 0, 1])
e15 = Element(tws5, [1, 1, 0, 0])

e16 = Element(tws5, [0, 1, 1, 1])
e17 = Element(tws5, [1, 1, 1, 0])




class EquivalenceTest(unittest.TestCase):
    def test_element_cover(self):
        self.assertEqual(e4.cover(e5), False)
        self.assertEqual(e4.cover(e8), True)
        self.assertEqual(e7.cover(e6), False)
        self.assertEqual(e9.cover(e5), True)
        self.assertEqual(e5.cover(e6), True)
        self.assertEqual(e6.cover(e6), True)
    
    def test_element_is_covered_by(self):
        self.assertEqual(e4.is_covered_by(e5), True)
        self.assertEqual(e4.is_covered_by(e6), False)
        self.assertEqual(e8.is_covered_by(e7), True)
    
    def test_rows_join(self):
        rows1 = [e4,e10,e8]
        rows2 = [e4,e11]
        rows3 = [e8]
        rows4 = [e8,e8]
        rows5 = [e9,e7,e6,e5,e4]
        rows6 = [e5,e6,e3]
        self.assertEqual(rows_join(rows1), [0,1,1,1])
        self.assertEqual(rows_join(rows2), [1,1,1,1])
        self.assertEqual(rows_join(rows3), [0,0,0,0])
        self.assertEqual(rows_join(rows4), [0,0,0,0])
        self.assertEqual(rows_join(rows5), [1,1,1,1])
        self.assertEqual(rows_join(rows6), [-1,-1,-1,-1])
    
    def test_element_is_composed(self):
        S = [e12,e13,e14,e15]
        S1 = [e12,e14,e15]
        self.assertEqual(e16.is_composed(S), True)
        self.assertEqual(e17.is_composed(S), True)
        self.assertEqual(e17.is_composed(S), True)
        self.assertEqual(e13.is_composed(S1), False)
        

if __name__ == "__main__":
    unittest.main()
