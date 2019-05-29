import math, json

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

class RuleSet:
    '''
        RuleSet loads rules from a json file
    '''
    def __init__(self, rules_filename):
        self._rules = {}
        with open(rules_filename, 'r') as rules_file:
            rules_json = json.loads(rules_file.read())
            for item_name, props in rules_json.items():
                try:
                    rule_lambda = eval(props['discount_rule'])
                    self._rules[item_name] = Rule( props['price'], eval(props['discount_rule']) )
                except Exception:
                    # We should probably raise an exception here, rather than leave the items out.
                    # However, while asked for production code, I'm not sure which context this is
                    # going to be used in and what the correct error handling flow would look like.
                    print('Rule %s cannot be evaluated'%item_name)

    def get(self, item_name, default):
        return self._rules.get(item_name, default)

    @property
    def rules(self):
        return self._rules

class Checkout:
    '''
        Checout scans items and applies pricing rules to give a correct
        total price.
    '''
    def __init__(self, ruleset):
        self._rules = ruleset
        self._items = {} # Checkout keeps counts in buckets as a dictionary

    def scan(self, *items):
        for item in items:
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
            else:
                # We should probably raise an exception here, rather than leave the items out.
                # However, while asked for production code, I'm not sure which context this is
                # going to be used in and what the correct error handling flow would look like.
                print('Warning: no rule found for %s, skipping items'%item_name)
                
        return total_price/100 # I chose to store prices in cents but we return them as euros

'''
    The rest is tests
'''
def test(products, ruleset):
    co = Checkout(ruleset)
    co.scan(*products)
    print('Items:', products)
    print('Total: ', co.total)
    return co.total

if __name__ == '__main__':
    rs = RuleSet('ruleset.json')

    assert test(['VOUCHER', 'TSHIRT', 'MUG'], rs) == 32.5
    assert test(['VOUCHER', 'TSHIRT', 'VOUCHER'], rs) == 25.0
    assert test(['TSHIRT', 'TSHIRT', 'TSHIRT', 'VOUCHER', 'TSHIRT'], rs) == 81.0
    assert test(['VOUCHER', 'TSHIRT', 'VOUCHER', 'VOUCHER', 'MUG', 'TSHIRT', 'TSHIRT'], rs) == 74.5
    assert test(['jamon', 'MUG', 'VOUCHER', 'VOUCHER', 'MUG', 'TSHIRT', 'TSHIRT', 'VOUCHER'], rs) == 65.0
