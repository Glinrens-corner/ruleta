from ruleta.exceptions import NoActionException
from collections import namedtuple




class Rule(namedtuple("Rule", ["if_", "then_"]) ):
    __slots__ = []
    
    def __call__(self, input_):
        if ( self.if_(input_)):
            return self.then_(input_)
        else:
            raise NoActionException()

         
