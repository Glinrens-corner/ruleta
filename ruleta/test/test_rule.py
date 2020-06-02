import unittest as ut
from ruleta.rule import Rule
from ruleta.exceptions import NoActionException

# example action factory
def value(val):
    return lambda input: val

#example condition
def false(input):
    return False

#example condition
def true(input):
    return True


class TestRule(ut.TestCase ):
    def test_members(self):
        "Rule has the members condition and action"
        new_rule = Rule(true, value(42))

        # with these memebers the actual input is irrelevant
        input_ = object()
        
        self.assertEqual(new_rule.if_(input_), True)
        self.assertEqual(new_rule.then_(input_), 42)
        
    def test_immutability(self):
        "A Rule is immutable"

        new_rule = Rule(true, value(42))
        
        with self.assertRaises(AttributeError):
            new_rule.if_ = false
        with self.assertRaises(AttributeError):
            new_rule.then_ = value(43)

    def test_iaction_1(self):
        "if the condition holds for the input, the action is applied to the input"

        new_rule = Rule(true , value(42))

        input_ = object()

        self.assertEqual(new_rule(input_), 42)


    def test_iaction_2(self):
        "if the condition does not hold for the input, the rule raises an NoActionException"

        new_rule = Rule(false , value(42))

        input_ = object()

        with self.assertRaises(NoActionException ):
            new_rule(input)
