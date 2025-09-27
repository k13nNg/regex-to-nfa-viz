from abc import ABC, abstractmethod

class Regex():
    def __init__(self):
        pass
    @abstractmethod
    def to_nfa():
        pass

class Concat(Regex):

    def __init__(self, left, right):
        self._left = left
        self._right = right
    
    def get_left(self):
        return self._left   
    
    def get_right(self):
        return self._right
    
    def __repr__(self):
        return f"Concat({self._left!r}, {self._right!r})"
    
class Union(Regex):
    def __init__(self, left: Regex, right: Regex):
        self._left = left
        self._right = right

    def get_left(self):
        return self._left   
    
    def get_right(self):
        return self._right
    
    def __repr__(self):
        return f"Union({self._left!r}, {self._right!r})"

class Star(Regex):
    def __init__(self, regex: Regex):
        self._regex = regex
    
    def __repr__(self):
        return f"Star({self._child!r})"

class Literal(Regex):
    def __init__(self, char: str):
        self._char = char

    def get_char(self):
        return self._char

    def __repr__(self):
        return f"Literal({self._char!r})"