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
    
    def to_nfa(self):
        '''
        return the NFA representation of the Concat operation
        '''

        # get the sub-NFA's
        left_nfa = self._left.to_nfa()
        right_nfa = self._right.to_nfa()

        # merge the sub-NFA's alphabets top create the alphabet for the new NFA
        output_nfa_alphabet = left_nfa.alphabet | right_nfa.alphabet

        # get the transition functions of the sub-NFA's
        left_nfa_trans_func = left_nfa.trans_func
        right_nfa_trans_func = right_nfa.trans_func

        # get the start and accept states
        output_nfa_start_state = left_nfa.start_state
        output_nfa_accept_state = right_nfa.accept_state

        # obtain the output states set
        output_nfa_states = {output_nfa_start_state, output_nfa_accept_state} | left_nfa.states | right_nfa.states

        # merge the transition functions of the sub-NFA's to create the transition function of the output NFA
        output_nfa_trans_func = left_nfa_trans_func | right_nfa_trans_func

        # create output NFA
        output_nfa = NFA(output_nfa_states, output_nfa_alphabet, output_nfa_start_state, 
        output_nfa_accept_state, output_nfa_trans_func)

        # add the epsilon-transition from the left sub-NFA accept state to the right sub-NFA start state)
        output_nfa.add_transition(left_nfa.accept_state, "@", right_nfa.start_state)

        return output_nfa
    
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
        return the NFA representation of the Union operation
        '''
        start_state = state_id_generator.get_new_id()
        accept_state = state_id_generator.get_new_id()
        
        left_nfa = self._left.to_nfa()
        right_nfa = self._right.to_nfa()

        left_nfa_trans_func = left_nfa.trans_func
        right_nfa_trans_func = right_nfa.trans_func

        # merge the sub-NFA's states and {start_state, accept_state} to create a new list of the states of NFA
        output_states = {start_state, accept_state} | left_nfa.states | right_nfa.states

        # merge the sub-NFA's alphabets top create the alphabet for the new NFA
        output_nfa_alphabet = left_nfa.alphabet | right_nfa.alphabet

        # merge the sub-NFA's transition function to create a new NFA
        output_nfa_trans_func = left_nfa_trans_func | right_nfa_trans_func

        output_nfa = NFA(output_states, output_nfa_alphabet, start_state, accept_state, output_nfa_trans_func)

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
    
    def to_nfa(self):
        '''
        return the NFA representation of the Star operation
        '''

        # get the sub-NFA
        sub_NFA = self._regex.to_nfa()

        # create new start and accept states
        output_nfa_start_state = state_id_generator.get_new_id()
        output_nfa_accept_state = state_id_generator.get_new_id()

        # the new nfa's alphabet will be the same as the sub-NFA's alphabet
        output_nfa_alphabet = sub_NFA.alphabet

        # create a new states set
        output_nfa_states = {output_nfa_start_state, output_nfa_accept_state} | sub_NFA.states

        # create the transition for the output NFA
        output_nfa_trans_func = sub_NFA.trans_func

        # create the output NFA
        output_nfa = NFA(output_nfa_states, output_nfa_alphabet, output_nfa_start_state, output_nfa_accept_state, output_nfa_trans_func)

        # add the necessary epsilon-transitions
        output_nfa.add_transition(output_nfa_start_state, "@", output_nfa_accept_state)
        output_nfa.add_transition(output_nfa_start_state, "@", sub_NFA.start_state)
        output_nfa.add_transition(sub_NFA.accept_state, "@", output_nfa_accept_state)
        output_nfa.add_transition(sub_NFA.accept_state, "@", sub_NFA.start_state)

        return output_nfa

    def __repr__(self):
        return f"Star({self._regex!r})"

class Epsilon(Regex):
    def to_nfa(self):
        '''
        construct the NFA for an empty string according to Thompson's rule
        '''
        start_state = state_id_generator.get_new_id()
        accept_state = state_id_generator.get_new_id()

        output_nfa = NFA({start_state, accept_state}, set(), start_state, accept_state)

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

        output_nfa = NFA({start_state, accept_state}, {self.char}, start_state, accept_state, {})

        output_nfa.add_transition(start_state, self._char, accept_state)

        return output_nfa

    def __repr__(self):
        return f"Literal({self._char!r})"
    
if __name__ == "__main__":
    test= Concat(Star(Literal("a")), Literal("b"))

    print(test.to_nfa())