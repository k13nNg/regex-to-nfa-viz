from abc import ABC, abstractmethod
from nfa import NFA, StateIDGenerator

state_id_generator = StateIDGenerator()

class Regex():
    def __init__(self):
        pass
    @abstractmethod
    def to_nfa():
        pass

class Concat(Regex):
    '''The concatenation operator'''

    def __init__(self, left, right):
        self._left = left
        self._right = right
    
    @property
    def left(self):
        return self._left   
    
    @property
    def right(self):
        return self._right
    
    def __repr__(self):
        return f"Concat({self._left!r}, {self._right!r})"
    
class Union(Regex):
    '''
    The union operator
    '''

    def __init__(self, left: Regex, right: Regex):
        self._left = left
        self._right = right

    @property
    def left(self):
        return self._left   
    
    @property
    def right(self):
        return self._right
    
    def to_nfa(self):
        '''
        return the NFA representation the Union operation
        '''
        start_state = state_id_generator.get_new_id()
        accept_state = state_id_generator.get_new_id()
        
        left_nfa = self._left.to_nfa()
        right_nfa = self._right.to_nfa()

        left_nfa_trans_func = left_nfa.trans_func
        right_nfa_trans_func = right_nfa.trans_func

        # merge the sub-NFA's states and {start_state, accept_state} to create a new list of the states of NFA
        output_states = {start_state, accept_state} | left_nfa.states | right_nfa.states

        # merge the sub-NFA's transition function to create a new NFA
        output_nfa_trans_func = left_nfa_trans_func | right_nfa_trans_func

        output_nfa = NFA(output_states, start_state, accept_state, output_nfa_trans_func)

        # add epsilon transition from output_nfa start state to the start states of left_nfa and right_nfa
        output_nfa.add_transition(start_state, "@", left_nfa.start_state)
        output_nfa.add_transition(start_state, "@", right_nfa.start_state)

        # add epsilon transition from end states of left_nfa and right_nfa to the end state of output_nfa

        # Note: we know that any NFA constructed by Thompson's Rule will have exactly 1 start state and 1 accept state
        output_nfa.add_transition(left_nfa.accept_state, "@", accept_state)
        output_nfa.add_transition(right_nfa.accept_state, "@", accept_state)

        return output_nfa

    def __repr__(self):
        return f"Union({self._left!r}, {self._right!r})"

class Star(Regex):
    '''The star operator'''

    def __init__(self, regex: Regex):
        self._regex = regex
    
    def __repr__(self):
        return f"Star({self._regex!r})"

class Epsilon(Regex):
    def to_nfa(self):
        '''
        construct the NFA for an empty string according to Thompson's rule
        '''
        start_state = state_id_generator.get_new_id()
        accept_state = state_id_generator.get_new_id()

        output_nfa = NFA({start_state, accept_state}, start_state, accept_state)

        return output_nfa

    def __repr__(self):

        return "Epsilon()"

class Literal(Regex):
    '''
    The literal operator
    '''

    def __init__(self, char: str):
        self._char = char

    @property
    def char(self):
        '''
        return the charactor of the Literal class
        '''

        return self._char
    
    def to_nfa(self):
        '''
        construct the NFA for a single literal according to Thompson's rule
        '''

        start_state = state_id_generator.get_new_id()
        accept_state = state_id_generator.get_new_id()

        output_nfa = NFA({start_state, accept_state}, start_state, accept_state, {})

        output_nfa.add_transition(start_state, self._char, accept_state)

        return output_nfa

    def __repr__(self):
        return f"Literal({self._char!r})"
    
if __name__ == "__main__":
    test = Union(Union(Literal("a"), Literal("b")), Literal("c"))

    print(test.to_nfa())