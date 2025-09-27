from abc import ABC, abstractmethod

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
    '''The union operator'''

    def __init__(self, left: Regex, right: Regex):
        self._left = left
        self._right = right

    @property
    def left(self):
        return self._left   
    
    @property
    def right(self):
        return self._right
    
    def __repr__(self):
        return f"Union({self._left!r}, {self._right!r})"

class Star(Regex):
    '''The star operator'''

    def __init__(self, regex: Regex):
        self._regex = regex
    
    def __repr__(self):
        return f"Star({self._regex!r})"

class Literal(Regex):
    '''The literal operator'''

    def __init__(self, char: str):
        self._char = char

    @property
    def char(self):
        return self._char

    def __repr__(self):
        return f"Literal({self._char!r})"