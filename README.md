# Ruleta

**Introduction**
Ruleta is a minimalist Python Rules framework based on functional programming 
principles.

Ruletas main goal is to make your rule definitions as close to the nested list
of rules that hopefully is your spec with a minimum amount of clutter.


E.g.[(examples/fizzbuzz.py)](https://github.com/Glinrens-corner/ruleta/blob/master/ruleta/examples/fizzbuzz.py):
```python
def fizzbuzz_rules0():
    """
    fizzbuzz; for each number:
    - return the number as string
    - but if the number is divisible_by 3 return "Fizz"
    - but if the number is divisible_by 5 return "Buzz"
    - but if the number is divisible_by 3 and 5 return "FizzBuzz"
    """  
    return Actionset(stringify)\
                 .but(Rule(divisible_by(3), value("Fizz")))\
                 .but(Rule(divisible_by(5), value("Buzz")))\
                 .but(Rule(AND(divisible_by(3),
                                divisible_by(5) ), value("FizzBuzz")))
```
# How To Use Ruleta
**Installation**
Currently Ruleta is only available as github repository. 
so use ```git clone https://github.com/Glinrens-corner/ruleta.git somewhere/in/your/PYTHONPATH```
or if you only want to use it in a specific project ``` git submodule add https://github.com/Glinrens-corner/ruleta.git somewhere/in/your/PYTHONPATH```
Ruleta has no other package dependencies (we aren't npm).

**Usage**
 1. Rewrite your spec into an unambiguous form of (possibly nested) bullet points of actions or rules (ruleta calls an action that only applies if a condition is met a rule).
    These rules can be joined by conjunctions: 
    * *but* this rule/action is an exception to all previous rules/actions.
    * *also* apply this action after previous actions.
    * *otherwise* apply this rule/action only if none of the previous rules applies.
 2. implement all conditions and actions you need.(see also interfaces)
    * conditions and actions should be stateless.
    * actions are more composable if they return the same type they consume.
    * actions are easier to reason about if they return a new instance instead of mutating the input.
    * actions and conditions can often be implemented efficiently via factory functions. E.g.:
```
# a condition factory
def divisible_by(x):
    return lambda val: val%x == 0
``` 
 
```
# a action factory
# it's intended use breaks the rule about composability
#   but for fizzbuzz composability  is not really needed.
def value(val):
    return lambda _: value 
```
 3. compose them according to your spec.

# Concepts
**Interfaces**
* *AbstractAction*: An AbstractAction is a callable that takes a single input, performs some action
  upon it and returns something. For the sake of sanity, an action should never be stateful. (Same input  should always result in the same result.
  It is up to the programmer if an action returns a different type as the
  input type. It should however be noted, that actions are more composable if
  they don't change type.
  If an AbstractAction performs no action, it must raise an
  NoActionException.
* *UnconditionalAction*: An UnconditionalAction is an AbstractAction that
  never raises a NoActionException.
	
* *Condition*: A Condition is a callable which transforms some input into a
  bool. It is formally a subtype of UnconditionalAction.

**Classes and Functions**

* *Rule*: A rule takes a Condition and an AbstractAction. It performs the
  action (and returns its return value) only if the condition evaluates to True. It otherwise
  raises an NoActionException. A Rule therfore implements the AbstractAction
  interface.
  E.g.:```Rule(divisible_by(3), value("Buzz"))```
* *combinators*: combinators are in the module ruleta.combinators. They are
  not by default exported from ruleta.
  * *ALL,AND*: ALL takes an arbitrary number of conditions and returns a
    condition which evaluates only to True if all passed conditions evaluate
    to True. AND is a convenient shorthand for ALL with exactly two
    conditions.
	E.g.:```Rule(AND(divisible_by(3),divisible_by(5)), value("FizzBuzz"))```
  * *ANY,OR*: ANY takes an arbitrary number of conditions and returns a
    condition which evaluates  to True if at least one passed conditions evaluates
    to True. OR is a convenient shorthand for ANY with exactly two
    conditions.
  * *NOT*: NOT takes a condition and returns a condition which evaluates to
    True exactly then when the original condition evaluates to False.

  * *ALSO*: ALSO combines **UnconditionalActions** . It takes an arbitrary
    amount of unconditional actions(which all need the same input and output
    type) and applies them sequentially. (The output of the first is fed to
    the second and so on...). User should keep the actions independent and not
    rely on the order of application.
	E.g. ```ALSO(set_quality(80),set_quality_change(0))```
	
* *Actionsets*: An actionset is a set of actions (Duh!) with a specific
  relation.
  *Note1*: action sets are not changed. Chaining another action creates a new
  actionset ( a BaseActionSet to be exact).
  *Note2*: action sets can currently not be mixed (except the default
  Actionset, which is compatible with any specialization). (otherwise the semantics
  were unclear) E.g. ``` Actionset(...).or_(...).but_(...) #!raises ActionsetBuildError```
  * *ActionSet*: Actionset simply executes its action. It implements a
    the same interface as the wrapped action. If no Action is supplied it
    wraps the identity action which simply returns its argument.(it doesn't
    raise NoActionException). As second argument an evaluator can be
    supplied. If no evaluator is supplied (or the evaluator is None, the
    ruleta.evaluation_strategies.default\_evaluator is used.
    It is also the basic action to which all other conjunctions are chained. 
    E.g. ``` ActionSet(stringify) ```
    * **conjunctions** The conjunctions an action set supports and their
          semantics are determined by the evaluator. The following are supplied by
          the built-in evaluator. 
	  (Note: all conjunctions (except the default conjunction "") take the
          form of methods on the BaseActionSet
          ```.conjunction(action)->BaseActionSet ```
	  (Note: the build-in evaluator only allows allows conjunctions of the
          same type to be chained. (except the default conjunction ""; all other
          conjunctions can be chained after the default conjunction) )
    * *but*: adding another action via the ```.but(action)``` method results in an exception to earlier rules.
           E.g.: in the fizzbuzz_rules0 example for 15 *only* the last rule is executed.
           E.g. see the examples/fizzbuzz.py
    * *also*:  The also conjunction is similar to the  ALSO  combinator 
          it applies the actions in order. Each to the output of the previous
          action. 
	  Different from ALSO actions queued by also  
 	  are  guraranted to execute from first to last and actions
          which raise an NoActionException are simply skipped (which may lead to all
          actions being skipped). 
	  If no Action is executed an NoActionException is raised.
    * *otherwise*: actions chained by otherwise are the similar to
          those chained by but. But the actions are tested in order (instead of
          reverse order) until one
          perfoms an action. Their result is returned.

**Advanced Interfaces**
  * *IEvaluator* The evaluator determines how action sets are evaluated.
    if the user wants to supply it's own evaluator, it has to implement the
    following properties and methods:
	
    * *allowed_conjunctions* this property is a list of strings determining
      all conjunctions this evaluator possibly allows. (The default conjunction "" should be included)
    * *accept(action_records, new_action_record )*: whenever a new
      action_record is queued this method is called to determine if it is
      accepted. if the method returns None, the record is accepted. If the
      method returns a string the string is used as error message for the
      ActionSetBuildError.
      *action_records* is the *list* of all previous set ActionRecords including the initial action record.
      *new_action_record* is the record that is tried to be newly added.
       Implementors should note that this method is called even on the first
       action during initialization of ActionSet. At that point *action_records* is an empty list and the empty string "" is
       used as an conjunction in *new_action_record*.
    * *evaluate(action_records, input_)*: this method is called when an
      ActionSet is applied to an input.
	

**AdvancedClasses**
* *Evaluator* : Ruleta has an build-in evaluator which allows the ActionSet the conjunctions
  listed above. 
* *ActionRecord*: An *ActionRecord* records an action (Duh).
   it is a namedtuple with the fields 
    *conjunction* (the name of the conjunction as a string) and 
    *action (the AbstractAction queue with this conjunction. ) 
* *default_evaluator* : a usersupplied evaluator can either be supplied on a
  per ActionSet basis or globally by setting ruleta.evaluation_strategies.default_evaluator
* *Exceptions*:Exceptions live in ruleta.exceptions and are not exported by
  default from the ruleta package.
   * *NoActionException*: This is an exception intended for internal use.
     It indicates that an action did not actually perform an action.
     It is detected and usually handled by the evaluator.
   * *ActionSetBuildError*: This error is thrown while *building* an
     actionset. To indicate that the actionset was build incorrectly (presumably the conjunctions can't be used in this order.).

	
	

