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
    
    def reset_id(self):
        self._id = 0

global_id_gen = StateIDGenerator()
    
class NFA: 
    '''
    NFA class

    Since we are using the Thompson's Rule to construct NFA's from a regex, we know for sure that each NFA will have exactly 1 start state and 1 accept state

    Attributes:
        - states: Set[Int] : Set of all the state ids
        - alphabet: Set[Str] : The alphabet of the NFA
        - start: Int : Id of the start state
        - accept: Int: Id of the accept state 
        - trans_func: Dict{(Int, Symbol) : Set[Int]} : Dictionary that map a pair of state id and symbol in the alphabet to another state (possible the same state)
    '''

    def __init__(self, states={}, alphabet={}, start=0, accept=0, trans_func = {}):
        '''
        initialize the NFA object 
        '''
        self._states = states
        self._alphabet = alphabet
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
    def alphabet(self):
        '''
        return the alphabet of the NFA
        '''
        return self._alphabet

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

    def get_next_state(self, curr_state, curr_char):
        '''
        return the set of the next state ids of curr_state, given the input curr_char. Return an empty set if there is no defined transition for curr_state on the input curr_char
        '''

        return self.trans_func.get((curr_state, curr_char), set())

    def get_epsilon_closure(self, states):
        '''
        return the epsilon closure of states
        '''

        stack = list(states)
        epsilon_closure = set(states)

        while (len(stack) > 0):
            state = stack.pop()

            if (state is not None):
                new_epsilon_closure = self.trans_func.get((state, "ε"), set())
                stack += list(new_epsilon_closure)
                epsilon_closure |= new_epsilon_closure

        return epsilon_closure


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

    def match(self, test_str):
        '''
        return True if the NFA accepts test_str, return False otherwise
        '''
        start_state = self.start_state
        curr_states = self.get_epsilon_closure({start_state})

        for ch in test_str:
            # optional: fail-fast if char not in alphabet
            if ch not in self.alphabet:
                return False

            # compute states reachable by consuming ch
            next_states = set()
            for s in curr_states:
                next_states |= self.get_next_state(s, ch)

            # if no next states, reject
            if not next_states:
                return False

            # now take epsilon-closure of those destinations only
            curr_states = self.get_epsilon_closure(next_states)

        # accept only if accept state is in the final closure
        return self.accept_state in curr_states


    def trace_match(self, test_str):
        """
        Generator that yields the set of active states after each character is processed.
        """
        curr_states = self.get_epsilon_closure({self.start_state})
        yield curr_states.copy()

        for ch in test_str:
            print(ch)
            if ch not in self.alphabet:
                yield set()  # empty = dead
                return

            next_states = set()
            for s in curr_states:
                next_states |= self.get_next_state(s, ch)

            curr_states = self.get_epsilon_closure(next_states)
            yield curr_states.copy()

            
