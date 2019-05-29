import math

class Rule:
    '''
        A pricing rule contains the price of an item
        and a lambda representing an items discount condition.
    '''
    def __init__(self, price, rule):
        self._price = price
        self._rule = rule

    def total(self, count):
        '''
            Currently discount rules are only based on item counts
            more complex rules would be interesting and require different
            parameters. If there is no rule, just return the price * count.
        '''
        if callable(self._rule):
            return self._rule(self._price, count)
        return self._price * count

# A ruleset comprised of item names and accompanying rules
RULES = {
    'VOUCHER':  Rule(500, (lambda price, count: math.ceil(count/2)*price)),
    'TSHIRT':   Rule(2000, lambda price, count: count*price if count<3 else count*1900),
    'MUG':      Rule(750, lambda price, count: count*price)
}

class Checkout:
    def __init__(self, rules=RULES):
        self._rules = rules
        self._items = {} # Checkout keeps counts in buckets as a dictionary

    def scan(self, item):
        item = item.upper() # I'm a lowercase kind of guy myself to be honest.

        # I like to inline things
        self._items[item] = self._items[item] + 1 if item in self._items.keys() else 1
        '''
            I could write it like this too if that's the prefereance
            if item in self._items.keys():
                self._items[item] = self._items[item] + 1
            else:
                self._items[item] = 1
        '''

    @property
    def total(self):
        total_price = 0
        for item_name, count in self._items.items():
            rule = self._rules.get(item_name, None)
            if isinstance(rule, Rule): # We can only calculate prices for items we have rules for
                total_price += rule.total(count)
        return total_price/100 # I chose to store prices in cents but we return them as euros

'''
    The rest is tests
'''
def test(products):
    co = Checkout()
    for product in products:
        co.scan(product)
    print('Items:', products)
    print('Total: ', co.total)
    return co.total

if __name__ == '__main__':
    assert test(['VOUCHER', 'TSHIRT', 'MUG']) == 32.5
    assert test(['VOUCHER', 'TSHIRT', 'VOUCHER']) == 25.0
    assert test(['TSHIRT', 'TSHIRT', 'TSHIRT', 'VOUCHER', 'TSHIRT']) == 81.0
    assert test(['VOUCHER', 'TSHIRT', 'VOUCHER', 'VOUCHER', 'MUG', 'TSHIRT', 'TSHIRT']) == 74.5
    assert test(['jamon', 'MUG', 'VOUCHER', 'VOUCHER', 'MUG', 'TSHIRT', 'TSHIRT', 'VOUCHER']) == 65.0
