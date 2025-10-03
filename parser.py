from regex import Regex, Union, Concat, Literal, Star, Epsilon

def parse_regex(s: str) -> Regex:
    pos = 0  # shared index

    def parse_union():
        # parse the union part
        nonlocal pos

        node = parse_concat()

        while pos < len(s) and s[pos] == '|':
            pos += 1
            right = parse_concat()
            node = Union(node, right)

        return node

    def parse_concat():
        # parse the concatenation part
        nonlocal pos

        node = parse_star()

        while pos < len(s) and s[pos] not in '|)':
            node = Concat(node, parse_star())

        return node

    def parse_star():
        # parse the star part
        nonlocal pos

        node = parse_atom()
        
        while pos < len(s) and s[pos] == '*':
            pos += 1
            node = Star(node)

        return node

    def parse_atom():
        # parse the literal part
        nonlocal pos

        if s[pos] == '(':
            pos += 1
            node = parse_union()
            if pos >= len(s) or s[pos] != ')':
                raise ValueError(f"Unmatched '(' at position {pos}")
            pos += 1
            return node
        
        elif s[pos] == "@":
            '''
            Use @ instead of epsilon for empty string
            '''
            pos += 1
            return Epsilon()
        
        else:
            char = s[pos]
            pos += 1
            return Literal(char)

    ast = parse_union()

    if pos != len(s):
        raise ValueError(f"Unexpected trailing input at position {pos}")
    
    return ast

if __name__ == "__main__":
    print(parse_regex(""))