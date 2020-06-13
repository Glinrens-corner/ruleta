from .exceptions import NoActionException,ActionSetBuildError
from collections import namedtuple



ActionRecord = namedtuple("ActionRecord", ["conjunction", "action"] )

class IEvaluator:
    def __init__(self):
        self.all_conjunctions = []

    def accept(self, action_records, new_action_record):
        pass

    def evaluate(self, action_records, input_):
        pass



class Evaluator(IEvaluator):
    _accepted_combinations = [ ("","but"),
                               ("","otherwise"),
                               ("","also"),
                               ("but","but"),
                               ("otherwise","otherwise"),
                               ("also", "also")]
    def __init__(self):
        self.accepted_conjunctions = ["","but","otherwise","also"]
    def accept(self, action_records, new_action_record):
        
        if len(action_records) == 0:
            if new_action_record.conjunction == "":
                return None
            else:
                return "Control-flow shouldn't reach here??"
        if (action_records[-1].conjunction, new_action_record.conjunction) in self._accepted_combinations:
            return None
        else:
            return "{0} cannot come after {1}".format(new_action_record.conjunction, action_records[-1].conjunction )

    def evaluate(self, action_records, input_):
        assert (len(action_records)>0)
        if action_records[-1].conjunction == "":
            assert(len(action_records)==1)
            return action_records[-1].action(input_)
        elif action_records[-1].conjunction == "but":
            assert all( [record.conjunction == "but" for record in action_records[1:] ])
            assert action_records[0].conjunction ==""
            for action_record in reversed(action_records):
                try:
                    return action_record.action(input_)
                except NoActionException:
                    pass
            else:
                raise NoActionException()
        elif action_records[-1].conjunction == "also":
            assert all( [record.conjunction == "also" for record in action_records[1:] ])
            assert action_records[0].conjunction ==""
            ret = input_
            performed_action = False
            for action_record in action_records:
                try:
                    
                    ret = action_record.action(ret )
                except NoActionException:
                    pass
                else:
                    performed_action = True
            if performed_action:
                return ret
            else:
                raise NoActionException()
        elif action_records[-1].conjunction == "otherwise":
            assert all( [record.conjunction == "otherwise" for record in action_records[1:] ])
            assert action_records[0].conjunction ==""
            for action_record in action_records:
                try:
                    return action_record.action(input_)
                except NoActionException:
                    pass
            else:
                raise NoActionException()
        else:
            raise ActionSetBuildError("unknown Error")

default_evaluator = Evaluator()

class BaseActionSet:
    def __init__(self,actions,evaluator):
        self._actions = actions
        self._evaluator = evaluator
        for conjunction in filter( lambda name:name != "",
        evaluator.accepted_conjunctions):
            setattr(self, conjunction, _conjunction_wrapper(self, conjunction))

    def __call__(self, input_):
        return self._evaluator.evaluate(self._actions, input_)

def _identity(input_):
    return input_

        
class ActionSet (BaseActionSet):
    
    def __init__(self, action=_identity, evaluator=None):
        evaluator = default_evaluator if evaluator is None else evaluator    
        error = evaluator.accept([], ActionRecord("",action))
        if error is not None:
            raise ActionSetBuildError(error)
        BaseActionSet.__init__(self,
                               [ActionRecord("",action)],
                               evaluator)





def _conjunction_wrapper(instance, next_conjunction):
    def conjunction(action):
        new_record = ActionRecord(next_conjunction,action)
        error = instance._evaluator.accept(instance._actions, new_record)
        if error is not None:
            raise ActionSetBuildError(error)
        return BaseActionSet(instance._actions+[new_record],
                                        instance._evaluator)
    return conjunction


