#!/usr/bin/env python3
""" Two methods for flexible dictionaries - better than defaultdict """
import pprint

# 1)
# From https://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries?noredirect=1&lq=1

class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


# 2)
# from https://stackoverflow.com/questions/2600790/multiple-levels-of-collection-defaultdict-in-python
class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

if __name__ == '__main__':
  d = Vividict()
  d['DE01']['name'] = 'West'
  d['DE01']['vals'] = [ 1, 2, 3 ]
  d['GB02']['ago'] = 1.2
  d['GB02']['ago'] += 1.2
  pprint.pprint(d)
