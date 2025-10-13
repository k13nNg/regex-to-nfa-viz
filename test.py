from regex import Literal, Union, Concat, Star

nfa = Concat(Star(Literal("a")), Star(Literal("b"))).to_nfa()

print(nfa.match("ba"))