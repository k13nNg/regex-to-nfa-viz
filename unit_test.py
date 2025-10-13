import unittest

# Import everything from your NFA module
# (adjust the import as needed)
from regex import Literal, Union, Concat, Star

class TestNFAMatch(unittest.TestCase):

    # -----------------------------
    # 1. Literal tests
    # -----------------------------
    def test_literal_match(self):
        nfa = Literal("a").to_nfa()
        self.assertTrue(nfa.match("a"))
        self.assertFalse(nfa.match(""))
        self.assertFalse(nfa.match("b"))

    # -----------------------------
    # 2. Concat tests
    # -----------------------------
    def test_concat_basic(self):
        nfa = Concat(Literal("a"), Literal("b")).to_nfa()
        self.assertTrue(nfa.match("ab"))
        self.assertFalse(nfa.match("a"))
        self.assertFalse(nfa.match("b"))
        self.assertFalse(nfa.match("abc"))

    def test_concat_nested(self):
        nfa = Concat(Concat(Literal("a"), Literal("b")), Literal("c")).to_nfa()
        self.assertTrue(nfa.match("abc"))
        self.assertFalse(nfa.match("ab"))
        self.assertFalse(nfa.match("a"))
        self.assertFalse(nfa.match("ac"))

    # -----------------------------
    # 3. Union tests
    # -----------------------------
    def test_union_basic(self):
        nfa = Union(Literal("a"), Literal("b")).to_nfa()
        self.assertTrue(nfa.match("a"))
        self.assertTrue(nfa.match("b"))
        self.assertFalse(nfa.match("c"))

    def test_union_nested(self):
        nfa = Concat(Union(Literal("a"), Literal("b")), Literal("c")).to_nfa()
        self.assertTrue(nfa.match("ac"))
        self.assertTrue(nfa.match("bc"))
        self.assertFalse(nfa.match("cc"))
        self.assertFalse(nfa.match("abc"))

    # -----------------------------
    # 4. Star tests
    # -----------------------------
    def test_star_basic(self):
        nfa = Star(Literal("a")).to_nfa()
        self.assertTrue(nfa.match(""))
        self.assertTrue(nfa.match("a"))
        self.assertTrue(nfa.match("aa"))
        self.assertTrue(nfa.match("aaaa"))
        self.assertFalse(nfa.match("b"))

    def test_star_nested(self):
        nfa = Star(Concat(Literal("a"), Literal("b"))).to_nfa()
        self.assertTrue(nfa.match(""))
        self.assertTrue(nfa.match("ab"))
        self.assertTrue(nfa.match("abab"))
        self.assertFalse(nfa.match("a"))
        self.assertFalse(nfa.match("abb"))

    # -----------------------------
    # 5. Combined tests
    # -----------------------------
    def test_combined_a_or_b_star_c(self):
        nfa = Concat(Star(Union(Literal("a"), Literal("b"))), Literal("c")).to_nfa()
        self.assertTrue(nfa.match("c"))
        self.assertTrue(nfa.match("ac"))
        self.assertTrue(nfa.match("bbc"))
        self.assertTrue(nfa.match("ababac"))
        self.assertFalse(nfa.match("ab"))
        self.assertFalse(nfa.match("cab"))

    def test_combined_a_b_or_c_star_d(self):
        nfa = Concat(Literal("a"), Concat(Star(Union(Literal("b"), Literal("c"))), Literal("d"))).to_nfa()
        self.assertTrue(nfa.match("ad"))
        self.assertTrue(nfa.match("abd"))
        self.assertTrue(nfa.match("acccd"))
        self.assertFalse(nfa.match("a"))
        self.assertFalse(nfa.match("ab"))
        self.assertFalse(nfa.match("acdX"))

    def test_combined_a_or_bc(self):
        nfa = Union(Literal("a"), Concat(Literal("b"), Literal("c"))).to_nfa()
        self.assertTrue(nfa.match("a"))
        self.assertTrue(nfa.match("bc"))
        self.assertFalse(nfa.match("b"))
        self.assertFalse(nfa.match("c"))

    # -----------------------------
    # 6. Edge cases
    # -----------------------------
    def test_edge_a_or_bc_star(self):
        nfa = Star(Union(Literal("a"), Concat(Literal("b"), Literal("c")))).to_nfa()
        self.assertTrue(nfa.match(""))
        self.assertTrue(nfa.match("a"))
        self.assertTrue(nfa.match("bc"))
        self.assertTrue(nfa.match("aabc"))
        self.assertFalse(nfa.match("ab"))

    def test_edge_a_star_b_star(self):
        nfa = Concat(Star(Literal("a")), Star(Literal("b"))).to_nfa()
        self.assertTrue(nfa.match(""))
        self.assertTrue(nfa.match("a"))
        self.assertTrue(nfa.match("b"))
        self.assertTrue(nfa.match("aaabb"))
        self.assertFalse(nfa.match("ba"))   

    # -----------------------------
    # 7. Invalid symbol
    # -----------------------------
    def test_invalid_symbol(self):
        nfa = Literal("a").to_nfa()
        self.assertFalse(nfa.match("A"))  # case-sensitive
        self.assertFalse(nfa.match(" "))

if __name__ == "__main__":
    unittest.main()