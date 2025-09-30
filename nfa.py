class NFA: 
    '''
    NFA class

    Attributes:
        - states: Set[Int] : Set of all the state ids
        - start: Int : Id of the start state
        - accept: Set[Int] : Set of all the accepting state ids
        - trans_func: Dict{(Int, Symbol) : Int} : Dictionary that map a pair of state id and symbol in the alphabet to another state (possible the same state)
    '''

    def __init__(self, states, start, accept, trans_func = None):
        '''
        initialize the NFA object 
        '''
        self._states = states
        self._start = start
        self._accept = accept

        if trans_func == None:
            self._trans_func = {}
        else:
            self._trans_func = trans_func

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
            # The pair key doesn't exist in trans_func => Create a new pair key and initilize {dest} as the value
            self._trans_func = {dest}
        else:
            # The pair key exists, so add dest into its set of next state ids
            self._trans_func[(src, sym)].add(dest)

    def __repr__(self):
        '''
        return a string representation of the NFA
        '''
        lines = []
        lines.append(f"States: {self._states}")
        lines.append(f"Starting states: {self._accept}")
        lines.append(f"Accepting states: {self._accept}")

        for (src, symbol), dests in self.transitions.items():
            lines.append(f"  {src} --{symbol}--> {dests}")
        
        return "\n".join(lines)


        