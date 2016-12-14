import itertools
import re


class DFA:
    def __init__(self,P_prime, Ei, alphabet, T ):
        self.alphabet = alphabet
        states = {}
        self.accept_states = {}
        for alpha in P_prime:
            state_name = repr(Ei[alpha])
            if state_name not in states.keys():
                states[state_name] = State(state_name)
            current_state = states[state_name]
            if len(state_name) == 0:
                for symbol in alphabet:
                    current_state.add_transition(symbol)
            else:
                for symbol in alphabet:
                    neighbor_state_name = repr(Ei[alpha + symbol])
                    if neighbor_state_name not in states.keys():
                        states[neighbor_state_name] = State(neighbor_state_name)
                    neighbor_state = states[neighbor_state_name]
                    current_state.add_transition(symbol, neighbor_state)
        self.states = states
        self.start_state = states[repr(Ei[''])]
        accept_state_keys = set()
        for alpha in T:
            if '' in Ei[alpha]:
                accept_state_keys.add(repr(Ei[alpha]))
        self.accept_states = {self.states[key] for key in accept_state_keys}

    def parse(self, string):
        tokens = list(string)
        q = self.start_state
        for token in tokens:
            q = q.transition(token)
        if q in self.accept_states:
            return 1
        return -1


# def f(a, b):
#     return a + b

# A is a DFA, P is a Language that is also live complete
def id(s_plus, alphabet, s_minus):
    i = 0
    v = []
    v.append('')
    V = set()
    V = V.union(set(['']))
    d_0 = 'd0'
    P_prime = s_plus.union(set([d_0]))
    T = s_plus.union(a + b for (a, b) in itertools.product(s_plus, alphabet))
    T_prime = T.union(set([d_0]))
    E = []
    E.append({})
    E[0][d_0] = set()

    for alpha in T:
        E[0][alpha] = set()
        if alpha in s_plus and alpha not in s_minus:
            E[0][alpha] = set([''])
        else:
            E[0][alpha] = set()

    # while (find_inconsistent_block(P, E, i) != None):
    while len(find_inconsistent_blocks(s_plus, E, i, alphabet)) > 0:
        j = i
        for (alpha, beta, b) in find_inconsistent_blocks(s_plus, E, i, alphabet):
            # print(repr(alpha) + ' ' + repr(beta) + ' ' + repr(i))
            # alpha, beta, b = find_inconsistent_block(P, E, i)
            r = E[i][alpha + b].symmetric_difference(E[i][beta + b])
            v.append([b + ri for ri in r][0])
            V = V.union({v[i + 1]})
            i += 1
            E.append({})
            for a in T_prime:
                if L(a + v[i]) is True:
                    E[i][a] = E[i - 1][a].union({v[i]})
                else:
                    E[i][a] = E[i - 1][a]
            i = j
        i = j + 1
    states = [E[i][a] for a in T]
    initial_state = E[i]['']
    accepting_states = set(itertools.chain(*(E[i][a] if '' in E[i][a] else '' for a in T)))
    return DFA(s_plus, E[i], alphabet, T)




def find_inconsistent_blocks(P, E, i, alphabet):
    triples = []
    for (alpha, beta) in itertools.product(P, P):
        for b in alphabet:
            if (E[i][alpha] == E[i][beta]) and (E[i][alpha + b] != E[i][beta + b]):
                triples.append((alpha, beta, b))
    return triples


def teacher(string):
    if re.search('\A(b|((aa)+))$', string) is not None:
        return True
    else:
        return False


def make_DFA(P_prime, Ei, alphabet):
    # maps Ei[a] to the State Object
    states = {}
    for alpha in P_prime:
        state_name = repr(Ei[alpha])
        if state_name not in states.keys():
            states[state_name] = State(state_name)
        current_state = states[state_name]
        if len(state_name) == 0:
            for symbol in alphabet:
                current_state.add_transition(symbol)
        else:
            for symbol in alphabet:
                neighbor_state_name = repr(Ei[alpha + symbol])
                if neighbor_state_name not in states.keys():
                    states[neighbor_state_name] =  State(neighbor_state_name)
                neighbor_state = states[neighbor_state_name]
                current_state.add_transition(symbol, neighbor_state)
    return states



class State:
    def __init__(self, string):
        self.string = string
        self.transitions = {}

    def add_transition(self,symbol, state=None):
        if state is None:
            self.transitions[symbol] = self
        else:
            self.transitions[symbol] = state

    def transition(self, symbol):
        if symbol not in self.transitions.keys():
            return self
        return self.transitions[symbol]


# P = set(['', 'a', 'b', 'aa'])
# alphabet = set(['a', 'b'])
#
# # dfa = id(P, alphabet, teacher)
# # print(repr(dfa.parse('b')))
# # print(repr(dfa.parse('bb')))
# # print(repr(dfa.parse('aaa')))
# # print(repr(dfa.parse('aaaa')))
# # print(repr(dfa.parse('aaaaaaaa')))
# # print(repr(dfa.parse('aaaabbaaaa')))

