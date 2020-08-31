"""
An implementation for the gilded rose kata as I understand it.

  https://github.com/NotMyself/GildedRose


"""
from collections import namedtuple
import unittest as ut
from ruleta import Rule, ActionSet
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
"""
The rules as written:
    `
  All items have a SellIn value which denotes the number of days we have to sell the item
  All items have a Quality value which denotes how valuable the item is
  At the end of each day our system lowers both values for every item

   Once the sell by date has passed, Quality degrades twice as fast
   The Quality of an item is never negative
   "Aged Brie" actually increases in Quality the older it gets
   The Quality of an item is never more than 50
   "Sulfuras", being a legendary item, never has to be sold or decreases in Quality
   "Backstage passes", like aged brie, increases in Quality as it's SellIn value approaches; Quality increases by 2 when there are 10 days or less and by 3 when there are 5 days or less but Quality drops to 0 after the concert
'



Just for clarification, an item can never have its Quality increase above 50, however "Sulfuras" is a legendary item and as such its Quality is 80 and it never alters.

"""

"""
The Rules as I understand them

The basic rules for the quality of all items are:
    every day the quality degrades by 1
    if the sellby date has passed the degradiation is doubled
    also if the item is conjured the degradiation is doubled also/again

but when the item is "Sulfuras" then it quality never changes
but also when the item is "Aged Brie" then the quality increases by every day by 1.
but also when the item is  "Backstage Passes" the the quality changes according to the following rules:
     the quality increases by 1 every day
     but if the sell by date is 10 days or less away, the quality increases by 2 each day
     but if the sell by date is even 5 days or less away the quality increases by 3 each day instead
     if the sellby date has passed, the quality is zero and never changes


independent of above rules the quality of an item would be below zero it is zero instead.
but if the items quality would be above 50 it is 50 instead.
but if the item is "Sulfuras" the quality is always 80  

""" 

basic_degradiation_rules= ActionSet(set_quality_change(-1))\
                             .also(Rule(sellby_date_passed, double_degradation))\
                             .also(Rule(is_item_conjured, double_degradation))
backstage_pass_rules = ActionSet(set_quality_change(+1))\
                           .but(Rule( days_until_sellby(leq(10) ), set_quality_change(+2)))\
                           .but(Rule( days_until_sellby(leq(5) ), set_quality_change(+3)))\
                           .but(Rule( sellby_date_passed, ALSO(set_quality(0),set_quality_change(0))))



extended_degradiation_rules = ActionSet(basic_degradiation_rules)\
                                  .but(Rule(is_aged_brie, set_quality_change(+1)) )\
                                  .but(Rule(is_sulfuras, set_quality_change(0)))\
                                  .but(Rule( is_backstage_passes, backstage_pass_rules ))




bracketing_rules = ActionSet(do_nothing)\
                       .but(Rule(compare_quality(leq(0)), set_quality(0)))\
                       .but(ActionSet(Rule(compare_quality(geq(50) ), set_quality(50))))
                       .but(Rule(is_sulfuras, set_quality(80)))
                                       


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

if __name__ == "__main__":
    ut.main()
