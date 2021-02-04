import unittest
import sys
sys.path.append('../')

from interval import Constraint
from nrta import Regionlabel
from nrtatable import Element, rows_join

rl1 = Regionlabel(0,"a", Constraint("[0,0]"))
rl2 = Regionlabel(0,"b", Constraint("[0,0]"))
rl3 = Regionlabel(10,"a", Constraint("[5,5]"))
rl4 = Regionlabel(8,"b", Constraint("[4,4]"))
rl5 = Regionlabel(14,"a", Constraint("[7,7]"))
rl6 = Regionlabel(4,"b", Constraint("[2,2]"))
rls0 = []  # empty
rls1 = [rl1]  # (a,0)
rls2 = [rl2]  # (b,0)
rls3 = [rl3]  # (a,5)
rls4 = [rl3, rl1]  # (a,5) (a,0)
rls5 = [rl3, rl2]  # (a,5) (b,0)
rls6 = [rl5]  # (a,7)
rls7 = [rl4]  # (b,4)
rls8 = [rl4, rl3]  # (b,4) (a,5)
rls9 = [rl1, rl1]  # (a,0) (a,0)
rls10 = [rl1, rl2]  # (a,0) (b,0)
rls11 = [rl6, rl3]  # (b,2) (a,5)
rls12 = [rl6]  # (b,2)

rl1 = Regionlabel(0,"a",Constraint("[0,0]"))
rl2 = Regionlabel(0,"b",Constraint("[0,0]"))

e0 = Element(rls0, [0])
e1 = Element(rls1, [0])
e2 = Element(rls2, [0])
e3 = Element(rls3, [1])
e4 = Element(rls4, [0, 1, 0, 1])
e5 = Element(rls5, [1, 1, 0, 1])
e6 = Element(rls5, [1, 0, 0, 1])
e7 = Element(rls5, [1, 0, 0, 0])
e8 = Element(rls5, [0, 0, 0, 0])
e9 = Element(rls5, [1, 1, 1, 1])
e10 = Element(rls5, [0, 0, 1, 0])
e11 = Element(rls5, [1, 0, 1, 0])

e12 = Element(rls5, [0, 1, 0, 0])
e13 = Element(rls5, [0, 1, 1, 0])
e14 = Element(rls5, [0, 1, 0, 1])
e15 = Element(rls5, [1, 1, 0, 0])

e16 = Element(rls5, [0, 1, 1, 1])
e17 = Element(rls5, [1, 1, 1, 0])

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