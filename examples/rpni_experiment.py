from dfalearn.rpni import *
from id import *

s_plus = ['b', 'aa', 'aaaa', 'aaba']
s_minus = ['', 'a', 'aaa', 'baa', 'ab']
alphabet = {'a', 'b'}

def rpni_experiment():
    dfa = rpni(s_plus, s_minus, alphabet)
    for s in s_plus:
        print(dfa[s])
    for s in s_minus:
        print(dfa[s])

def id_experiment():
    dfa = id(set(s_plus), alphabet, s_minus)


rpni_experiment()





# dfa = rpni(s_plus, s_minus, {'a', 'b'})

# for s in s_plus:
#     print(dfa[s])
#
# for s in s_minus:
#     print(dfa[s])