# Ruleta

Ruleta is a minimalist Python Rules framework based on functional programming 
principles.

Ruletas main goal is to make your rule definitions as close to the nested list
of rules that hopefully is your spec with a minimum amount of clutter.


E.g.:
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
                 .but_(Rule(divisible_by(3), value("Fizz")))\
                 .but_(Rule(divisible_by(5), value("Buzz")))\
                 .but_(Rule(AND(divisible_by(3),
                                divisible_by(5) ), value("FizzBuzz")))
```

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
  bool. It is formally a subtype of UnconditionalAction this is currently
  never made use of.

**Classes and Functions**

* *Rule*: A rule takes a Condition and an UnconditionalAction. It performs the
  action (and returns its return value) only if the condition evaluates to True. It otherwise
  raises an NoActionException. A Rule therfore implements the AbstractAction
  interface.
  E.g.:```python Rule(divisible_by(3), value("Buzz"))```
* *combinators*: combinators are in the module ruleta.combinators. They are
  not by default exported from ruleta.
  * *ALL,AND*: ALL takes an arbitrary number of conditions and returns a
    condition which evaluates only to True if all passed conditions evaluate
    to True. AND is a convenient shorthand for ALL with exactly two
    conditions.
	E.g.:```python Rule(AND(divisible_by(3),divisible_by(5)), value("FizzBuzz"))```
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
	E.g. ```python ALSO(set_quality(80),set_quality_change(0))```
	
* *Actionsets*: An actionset is a set of actions (Duh!) with a specific
  relation.
  *Note1*: action sets are immutable. Chaining another action creates a new
  actionset.
  *Note2*: action sets can currently not be mixed (except the default
  Actionset, which is compatible with any specialization). (otherwise the semantics
  were unclear) E.g. ```python Actionset(...).or_(...).but_(...) #!raises ActionsetBuildError```
  * *Actionset*: Actionset simply executes its action. It implements an
    the same interface as the wrapped action.
	E.g. ```python Actionset(stringify) ```
  * *ActionWithExceptions* ActionWithExceptions is normally
	created by adding another action via the ```.but_()``` method.
	The default action (from the Actionset constructor) is only executed if
	all exceptions perform no action.
    ActionWithExceptions implements an AbstractAction or
    UnconditionalAction depending on the type of the default action.
	**NOTE** It is assumed that later exceptions are more specific and
    override earliers exceptions. E.g.: in the fizzbuzz_rules0 example for 15 *only*
    the last rule is executed.
	E.g. see the examples/fizzbuzz.py
  * *ChainedActions*:  ChainedActions is similar to the ALSO  combinator 
    it applies the actions in order. Each to the output of the previous
    action. 
	Different from ALSO ChainedActions 
    gurarantees the order of execution is first to last action and actions
    which raise an NoActionException are simply skipped (which may lead to all
    actions being skipped). 
    It is also normally created via the ```also_``` method. 
	ChainedActions implements the UnconditionalAction interface.
  * *AlternativeActions*: AlternativeActions is the similar to
    ActionWithExceptions. But the actions are tested in order until one
    perfoms an action. Their result is returned.
* *Exceptions*:Exceptions live in ruleta.exceptions and are not exported by
  default from the ruleta package.
   * *NoActionException*: This is an exception intended for internal use.
     It indicates that an action did not actually perform an action.
     It is detected and used by several Actionset specializations.
   * *ActionsetBuildError*: This error is thrown while *building* an
     actionset. To indicate that the actionset was illegally build.

	
	

