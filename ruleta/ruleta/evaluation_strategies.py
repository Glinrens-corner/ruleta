from .exceptions import NoActionException

class Actionset:
    def __init__(self, action):
        self._action = action
        
    def but_(self, action):
        return ActionWithExceptions(self._action, [action])

    def also_(self, action):
        return ChainedActions([self._action,action])

    def or_(self, action):
        return AlternativeActions([self._action, action])

    def __call__(self, input_):
        return self._action(input_)

class ActionWithExceptions:
    def __init__(self, default_action, exceptions):
        self._default_action = default_action
        self._exceptions = exceptions

    def but_(self, exception):
        return ActionWithExceptions(self._default_action,
                                    self._exceptions+ [exception])
    
    def also_(self, action):
        raise ActionsetBuildError("cannot chain a chained action (also_) after an exception (but_)")

    def or_(self, action):
        raise ActionsetBuildError("cannot chain an alternative action (or_) after an exception (but_)")

    def __call__(self, input_):
        for exception in reversed(self._exceptions):
            try:
                ret = exception(input_)
            except NoActionException:
                pass
            else:
                return ret
        return self._default_action(input_)

class ChainedActions:
    def __init__(self, actions):
        self._actions = actions

    def but_(self, action):
        raise ActionsetBuildError("cannot chain an exception (but_) after a chained action (also_)")

    def also_(self, action):
        return ChainedActions(self._actions+[action ])

    def or_(self, action):
        raise ActionsetBuildError("cannot chain an alternative action (or_) after an chained action (also_)")

    def __call__(self, input_):
        val = input_
        for action in self._actions:
            try:
                val = action(val)
            except NoActionException:
                pass
        return val

    

class AlternativeActions:
    def __init__(self, actions):
        self._actions = actions

    def but_(self, exception):
        raise ActionsetBuildError("cannot chain an exception (also_) after an alternative action (or_)")
    
    def also_(self, action):
        raise ActionsetBuildError("cannot chain a chained action (also_) after an alternative_ action)")

    def or_(self, action):
        return AlternativeActions(self._actions + [action])

    def __call__(self, input_):
        for action in self._actions:
            try:
                ret = action(input_)
            except NoActionException:
                pass
            else:
                return ret
        raise NoActionException()
