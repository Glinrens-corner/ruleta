

def ALL(*conditions):
    return lambda input_ : all(condition(input_) for condition in conditions)

def AND( first, second):
    return ALL(first, second)

def ANY(*conditions):
    return lambda input_ : any(condition(input_) for condition in conditions)

def OR(first, second):
    return ANY(first,second)




def ALSO(*actions):
    def ALSO_(input_):
        val = input_
        for action in actions:
            val = action(val)
        return val
    return ALSO_
