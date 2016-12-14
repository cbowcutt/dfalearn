from dfalearn.rpni import *

s_plus = ['b', 'aa', 'aaaa', 'aaba']
s_minus = ['', 'a', 'aaa', 'baa', 'ab']
alphabet = {'a', 'b'}

# construct a DFA object
dfa = rpni(s_plus, s_minus, alphabet)

# run the dfa on input that the dfa accepts
[print(dfa[s]) for s in s_plus]
# run the dfa on the input that the dfa rejects
[print(dfa[s]) for s in s_minus]

