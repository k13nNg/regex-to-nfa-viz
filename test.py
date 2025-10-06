from parser import parse_regex

raw_regex = "(a|bc)*"

parsed_regex = parse_regex(raw_regex)

parsed_regex_nfa = parsed_regex.to_nfa() 

assert(parsed_regex_nfa.match("abababab") == False)
assert(parsed_regex_nfa.match("aaaaaaaaa") == True)
assert(parsed_regex_nfa.match("abc") == True)
assert(parsed_regex_nfa.match("abcaaaaaaaa") == True)
assert(parsed_regex_nfa.match("bcbcaabc") == True)
assert(parsed_regex_nfa.match("") == True)
assert(parsed_regex_nfa.match("aba") == False)

print(parsed_regex_nfa.match("xxabcxx"))