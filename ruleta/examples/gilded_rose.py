"""

  
 Basic Degradiation Rules:
  - every day the quality degrades by 1
  - And  if the sellby_date has passed, quality degrades twice  as fast
  - And if the item is conjured the quality degrades twice as fast
 - But "Aged Brie" increases in Quality the older it gets
 - But "Sulfuras" never decreases in Quality
 - But if the item is "Backstage passes" the quality changes as follows:
        - quality always increases by 1
        - but if the sellby_date 10 days or less away , quality increases by 2
        - but if the sellby_date 5 days or less away , quality increases by 3
        - but if the sellby_date has passed, the quality is and stays 0.

 


 
"""
from collections import namedtuple
import unittest as ut
from ruleta import Rule, Actionset
from ruleta.combinators import ALSO
import re

ItemRecord = namedtuple("ItemRecord",["name", "quality", "quality_change", "sellin" ] )

def print_through(label, condition):
    def print_through_(input_):
        val=condition(input_)
        print(label, val)
        return val
    return print_through_

def set_quality_change(val):
    return lambda item_record: item_record._replace(quality_change=val)

def sellby_date_passed(item_record):
    return item_record.sellin <=0

def multiply_quality_change(val):
    return lambda item_record: item_record._replace(quality_change = item_record.quality_change*val )

def does_item_degrade (item_record):
    return item_record.quality_change <0

def is_item_conjured(item_record ):
    return bool(re.match("conjured", item_record.name))

def is_aged_brie(item_record):
    return item_record.name == "Aged Brie"

def is_sulfuras(item_record):
    return item_record.name == "Sulfuras"

def is_backstage_passes(item_record):
    return item_record.name == "Backstage passes"

def days_until_sellby(condition):
    return lambda item_record: condition(item_record.sellin)

def leq(val):
    return lambda input_ : input_ <= val

def geq(val):
    return lambda input_ : input_ >= val

double_degradation = Rule(does_item_degrade, multiply_quality_change(2))

def set_quality(val):
    return lambda item_record: item_record._replace(quality=val)

def do_nothing(item_record):
    return item_record

def compare_quality(condition ):
    return lambda item_record : condition(item_record.quality)


# Rulesets 

backstage_pass_rules = Actionset(set_quality_change(+1))\
                           .but_(Rule( days_until_sellby(leq(10) ), set_quality_change(+2)))\
                           .but_(Rule( days_until_sellby(leq(5) ), set_quality_change(+3)))\
                           .but_(Rule( sellby_date_passed, ALSO(set_quality(0),set_quality_change(0))))


basic_degradiation_rules= Actionset(set_quality_change(-1))\
                             .also_(Rule(sellby_date_passed, double_degradation))\
                             .also_(Rule(is_item_conjured, double_degradation))

extended_degradiation_rules = Actionset(basic_degradiation_rules)\
                                  .but_(Rule(is_aged_brie, set_quality_change(+1)) )\
                                  .but_(Rule(is_sulfuras, set_quality_change(0)))\
                                  .but_(Rule( is_backstage_passes, backstage_pass_rules ))




bracketing_rules = Actionset(do_nothing)\
                       .but_(Rule(compare_quality(leq(0)), set_quality(0)))\
                       .but_(Actionset(Rule(compare_quality(geq(50) ), set_quality(50)))
                                 .but_(Rule(is_sulfuras, set_quality(80))))
                                       


class GildedRose:
    def __init__(self, items):
        self._items = items
        
    def update_quality(self):
        for i in range(0,len(self._items)):
            self._items[i] = self._update_item(self._items[i])
        

    def _update_item(self, item):
        item_record = extended_degradiation_rules(
            ItemRecord( item.name, item.quality, 0, item.sellin) )
        item_record = bracketing_rules( item_record._replace(quality=item_record.quality+item_record.quality_change ) )
        return Item(item_record.name, max(item_record.sellin-1,0), item_record.quality)


class Item:
    def __init__(self, name, sellin, quality):
        self.name = name
        self.sellin = sellin
        self.quality = quality

        
    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sellin, self.quality)

class TestGildedRose(ut.TestCase):
    def test_standard_item(self):
        gilded_rose = GildedRose([Item("a Sword", 100, 5)])

        gilded_rose.update_quality( )

        self.assertEqual( ["a Sword, 99, 4"], list(map(repr,gilded_rose._items)))

    def test_conjured_item(self):
        gilded_rose = GildedRose([Item("conjured Sword", 100, 5)])

        gilded_rose.update_quality( )

        self.assertEqual( ["conjured Sword, 99, 3"], list(map(repr,gilded_rose._items)))

    def test_minimum_quality(self):
        gilded_rose = GildedRose([Item("a Sword", 100, 0)])

        gilded_rose.update_quality( )

        self.assertEqual( ["a Sword, 99, 0"], list(map(repr,gilded_rose._items)))

    def test_backstage_passes_10_days(self):
        gilded_rose = GildedRose([Item("Backstage passes", 10, 5)])

        gilded_rose.update_quality( )

        self.assertEqual( ["Backstage passes, 9, 7"], list(map(repr,gilded_rose._items)))

    def test_backstage_passes_5_days(self):
        gilded_rose = GildedRose([Item("Backstage passes", 5, 5)])

        gilded_rose.update_quality( )

        self.assertEqual( ["Backstage passes, 4, 8"], list(map(repr,gilded_rose._items)))

    def test_backstage_passes_0_days(self):
        gilded_rose = GildedRose([Item("Backstage passes", 0, 5)])

        gilded_rose.update_quality( )

        self.assertEqual( ["Backstage passes, 0, 0"], list(map(repr,gilded_rose._items)))

