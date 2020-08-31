import unittest as ut
from ruleta import Rule, ActionSet
from ruleta.combinators import AND


# This is formally an action factory. It factories an action ;).
# The action ignores the input_ and replaces it with the preconfigured value.
# E.g.: 
# replace_with_fizz = value("Fizz")
# replace_with_fizz(3) == "Fizz"
def value(val):
    return lambda input_: val

# This is formally an condition factory. It builds a condition.
# The condition checks if the input is divisible by the preconfigured value.
# E.g.: 
# divisible_by_3 = divisible_by(3)
# divisible_by_3(99) == True
def divisible_by(val):
    return lambda input_: input_%val == 0

#another action
#an action should have an actiony name
stringify = str



#Three different ways to formulate the fizzbuzz rules:


def fizzbuzz_rules0():
    """
    fizzbuzz; for each number:
    - return the number as string
    - but if the number is divisible_by 3 return "Fizz"
    - but if the number is divisible_by 5 return "Buzz"
    - but if the number is divisible_by 3 and 5 return "FizzBuzz"
    """  
    return ActionSet(stringify)\
                 .but(Rule(divisible_by(3), value("Fizz")))\
                 .but(Rule(divisible_by(5), value("Buzz")))\
                 .but(Rule(AND(divisible_by(3),
                                divisible_by(5) ), value("FizzBuzz")))

def fizzbuzz_rules1():
    """
    fizzbuzz; for each number appliy the first applicable rule:
    - if the number is divisible_by 3 and 5 return "FizzBuzz"
    - if the number is divisible_by 3 return "Fizz"
    - if the number is divisible_by 5 return "Buzz"
    - otherwise return the number as string
    """  
    return ActionSet(Rule(AND(divisible_by(3),divisible_by(5) ), value("FizzBuzz")))\
        .otherwise(Rule(divisible_by(3), value("Fizz")) )\
        .otherwise(Rule(divisible_by(5), value("Buzz")))\
        .otherwise(stringify)

def fizzbuzz_rules2():
    """
    fizzbuzz; for each number appliy the first applicable rule:
    - if the number is divisible_by 3 do one of the following:
               - if the number is also divisible by 5 return "FizzBuzz"
               - otherwise return "Fizz"
    - if the number is divisible_by 5 return "Buzz"
    - otherwise return the number as string
    """  
    return ActionSet(Rule(divisible_by(3), 
                                    ActionSet(Rule(divisible_by(5), value("FizzBuzz")))
                                    .otherwise(value("Fizz"))))\
                     .otherwise(Rule(divisible_by(5), value("Buzz")))\
                     .otherwise(stringify)



class TestFizzbuzz(ut.TestCase):
    expected = ["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz",
                "16","17","Fizz","19","Buzz","Fizz","22","23","Fizz","Buzz","26","Fizz","28","29","FizzBuzz",
                "31","32","Fizz","34","Buzz","Fizz","37","38","Fizz","Buzz","41","Fizz","43","44","FizzBuzz",
                "46","47","Fizz","49","Buzz","Fizz","52","53","Fizz","Buzz","56","Fizz","58","59","FizzBuzz",
                "61","62","Fizz","64","Buzz","Fizz","67","68","Fizz","Buzz","71","Fizz","73","74","FizzBuzz",
                "76","77","Fizz","79","Buzz","Fizz","82","83","Fizz","Buzz","86","Fizz","88","89","FizzBuzz",
                "91","92","Fizz","94","Buzz","Fizz","97","98","Fizz","Buzz"]

    def test_fizzbuzz0(self):
        fizzbuzz = fizzbuzz_rules0()

        self.assertEqual(self.expected, [ fizzbuzz(i) for i in range(1,101)])

    def test_fizzbuzz1(self):
        fizzbuzz = fizzbuzz_rules1()

        self.assertEqual(self.expected, [ fizzbuzz(i) for i in range(1,101)])

    def test_fizzbuzz2(self):
        fizzbuzz = fizzbuzz_rules2()

        self.assertEqual(self.expected, [ fizzbuzz(i) for i in range(1,101)])

if __name__ == "__main__":
    ut.main()
