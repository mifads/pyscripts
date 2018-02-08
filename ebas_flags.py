#!/usr/bin/python3
import os.path
# tip from https://stackoverflow.com/questions/38368956/perls-data-equivalent-in-python
current_dir = os.path.dirname(os.path.abspath(__file__))

def get_ebasflags():
  """ returns a dictionary of Ebas flags associated with a given flag number.
      Note that we keep the numbers as string, as returned by split  """
  flags=dict()
  with open(os.path.join(current_dir, 'ebas_flags.txt')) as data:
    for line in data:
       if line.startswith('#'): continue
       #print(line)
       num, flag, rest = line.split(maxsplit=2)
       flags[num] = flag
       print(num, flag, flags[num] )
  return flags
