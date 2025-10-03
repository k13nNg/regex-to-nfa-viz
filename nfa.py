class StateIDGenerator:
    '''
    StateIDGenerator represents a generator for state id, return a new id for a state everytime get_id() is called
    -> Guarantees each state has a unique id
    '''
    def __init__(self):
        self._id = 0
    def get_new_id(self):
        self._id += 1

        return self._id
    
class NFA: 
    '''
    NFA class

    Since we are using the Thompson's Rule to construct NFA's from a regex, we know for sure that each NFA will have exactly 1 start state and 1 accept state

    Attributes:
        - states: Set[Int] : Set of all the state ids
        - start: Int : Id of the start state
        - accept: Int: Id of the accept state 
        - trans_func: Dict{(Int, Symbol) : Int} : Dictionary that map a pair of state id and symbol in the alphabet to another state (possible the same state)
    '''

    def __init__(self, states, start, accept, trans_func = {}):
        '''
        initialize the NFA object 
        '''
        self._states = states
        self._start = start
        self._accept = accept

        self._trans_func = trans_func

    @property
    def start_state(self):
        '''
        return the start state of the NFA
        '''
        return self._start
    
    @property
    def accept_state(self):
        '''
        return the accept states of the NFA
        '''
        return self._accept

    @property
    def trans_func(self):
        '''
        return the transition map/ function of the NFA
        '''

        return self._trans_func
    
    @property
    def states(self):
        '''
        return the states of the NFA
        '''

        return self._states

    def add_states(self, id):
        '''
        add a state into the NFA's states set, raise error if the state already exists

        id: Int: Id of the new state
        '''

        if not(id in self._states):
            self._states.add(id)
        else:
            raise ValueError("State already exists")

    def add_transition(self, src, sym, dest):
        '''
        add a transition to the NFA's transition function, raise error if either src or dest doesn't exist in the NFA

        src: Int: id of the src state
        sym: Char: the symbol in the alphabet
        dest: Int: id of the next state
        '''

        # check if the states exist in the NFA, raise error if either of them don't
        if not(src in self._states and dest in self._states):
            raise ValueError(f"Invalid transition: {src} or {dest} does not exist in states")
        
        # add the transition to trans_func
        if not((src, sym) in self._trans_func):
            # The pair key doesn't exist in trans_func => Create a new pair key and initialize {dest} as the value
            self._trans_func[(src, sym)] = {dest}
        else:
            # The pair key exists, so add dest into its set of next state ids
            self._trans_func[(src, sym)].add(dest)

    def __repr__(self):
        '''
        return a string representation of the NFA
        '''
        lines = []
        lines.append(f"States: {self._states}")
        lines.append(f"Starting states: {self._start}")
        lines.append(f"Accepting states: {self._accept}")

        for (src, symbol), dests in self._trans_func.items():
            for d in dests:
                lines.append(f"  {src} --{symbol}--> {d}")
        
        return "\n".join(lines)


        