import itertools
import re
import copy


# based on the algorithm by Rajesh Parekh and Vasant Honavar
def rpni(s_plus, s_minus, alphabet):
    # state Merging
    dfa = constructPTA(s_plus, alphabet)
    keys = list(dfa.Q.keys())
    keys_to_remove = set()
    for i in range(1, len(keys)):
        if keys[i] is None:
            continue
        for j in range(0, i):
            if keys[j] is None:
                continue
            copy_dfa = copy.deepcopy(dfa)
            new_dfa = reduce_dfa(copy_dfa, keys[i], keys[j])
            neg_results = [new_dfa[s] for s in s_minus]
            pos_results = [new_dfa[s] for s in s_plus]
            print(neg_results)
            if 1 not in neg_results and -1 not in pos_results:
                dfa = new_dfa
                keys[i] = None
                keys[j] = None
                break
    return dfa


def reduce_dfa(dfa, i, j):
    delta, q_merged = merge_states(dfa, i, j)
    dfa.delta = delta
    dfa.Q[q_merged.id] = q_merged
    dfa.Q.pop(i)
    dfa.Q.pop(j)
    if i in dfa.F.keys():
        dfa.F.pop(i)
    if j in dfa.F.keys():
        dfa.F.pop(j)
    return dfa


def merge_states(dfa, i, j):
    qi = dfa.Q[i]
    qj = dfa.Q[j]
    q_merged = DFA.State(repr(qi.id + qj.id))
    if qi.id in dfa.F.keys() or qj.id in dfa.F.keys():
        dfa.F[q_merged.id] = q_merged
    if dfa.q0 is qi or dfa.q0 is qj:
        dfa.q0 = q_merged
    delta, q_merged = merge_transitions(dfa.delta, [qi, qj], q_merged)
    if i in q_merged.parent_ids:
        q_merged.parent_ids.remove_parent_id(i)
    if j in q_merged.parent_ids:
        q_merged.remove_parent_id(j)
    return delta, q_merged


def merge_transitions(delta, q, q_merged):
    for qi in q:
        transitions_from_qi = delta.get_transitions_from_state(qi.id)
        for (id, token) in transitions_from_qi:
            q_merged.add_child_id(id)
            delta[(q_merged.id, token)] = delta[(id, token)]
            delta.pop((id, token))
        transitions_to_qi = delta.get_transitions_to_state(qi.id)
        for (id, token) in transitions_to_qi:
            q_merged.add_parent_id(id)
            delta[(id, token)] = q_merged
    return delta, q_merged


#s_plus should be an ordered list
def constructPTA(s_plus, alphabet):
    Q = {}
    F = {}
    q0 = DFA.State('')
    Q[q0.id] = q0
    delta = DFA.Delta()
    for s in s_plus:
        q = q0
        for c in s:
            qNext = delta[q.id, c]
            if qNext is None:
                qNext = DFA.State(q.id + c)
                # connect the states
                q.add_child_id(qNext.id)
                qNext.add_parent_id(q.id)
                delta[(q.id, c)] = qNext
                Q[q.id] = q
            q = qNext
        F[q.id] = q
    return DFA(Q, alphabet, q0, delta, F)


class Block:
    def __init__(self, states):
        self.states = states

    def is_equivalent_to_(self, other_block):
        pass


class DFA:
    def __init__(self, Q, Sigma, q0, delta, F):
        # State.id -> State
        self.Q = Q
        # set of symbols
        self.Sigma = Sigma
        # start State
        self.q0 = q0
        # (State.id, symbol) -> State
        self.delta = delta
        # State.id, symbol -> State
        self.F = F

    def __copy__(self):
        return DFA(dict(self.Q), set(self.Sigma), self.q0, self.delta, self.F)

    def __getitem__(self, item):
        q = self.q0
        for token in item:
            q = self.delta[(q.id, token)]
            if q is None:
                return -1
        if q.id in self.F.keys():
            return 1
        else:
            return -1

    def partition(self, i):
        new_Q = {}
        q0 = DFA.State(i.id)
        new_Q[i.id] = q0
        delta = {}
        q = q0
        for (child_id, token) in self.delta.get_transitions_from_state(q.id):
            child_q = DFA.State(child_id)
            delta[(q.id, token)] = child_q
            q.add_child_id(child_id)
            child_q.add_parent_id(q.id)

    def mark_pairs_with_final_states(self, pairs):
        pairs_with_final_state = []
        for pair in pairs:
            if pair[0] in self.F or pair[1] in self.F:
                pairs_with_final_state.append(pair)

    def parent_child_pairs(self):
        pairs = []
        for (id1, id2) in itertools.product(self.Q.keys(), self.Q.keys()):
            q1 = self.Q[id1]
            q2 = self.Q[id2]
            if q1.has_child(id2):
                pairs.append((id1, id2))
        return set(pairs)

    class State:
        def __init__(self, id):
            self.id = id
            # contains the id of parents
            self.parent_ids = set()
            # contains the id of childre
            self.child_ids = set()

        def add_parent_id(self, parent_id):
            self.parent_ids.add(parent_id)

        def remove_parent_id(self, parent_id):
            self.parent_ids.remove(parent_id)


        def add_child_id(self, child_id):
            self.child_ids.add(child_id)

        def add_remove_child_id(self, child_id):
            self.child_ids.remove(child_id)

        def has_child(self, id):
            if id in self.child_ids:
                return True
            return False

    class Delta:
        def __init__(self):
            # State.id X key -> State.id
            self.map = {}

        # #item is id
        def __getitem__(self, item):
            if item not in self.map.keys():
                return None
            else:
                return self.map[item]

        def __setitem__(self, key, value):
            self.map[key] = value

        def get_transitions_from_state(self, id):
            pairs = []
            for (_id, token) in self.map.keys():
                if _id is id:
                    pairs.append((_id, token))
            return pairs

        def get_transitions_to_state(self, id):
            pairs = []
            for (_id, token), image in self.map.items():
                if image.id is id:
                    pairs.append((_id, token))
            return pairs

        def pop(self, pair):
            self.map.pop(pair)





# def block(i, partition):
#     return partition[i]
#
#
# def derive(M, partition):
#     pass
#
#
# def order_strings(s):
#     pass
#
#
# def maximum_length(s):
#     return max(s, key= lambda si: len(si))
#
#
# class Block:
#     def __init__(self, key, states):
#         self.key = key
#         self.states = states
#
#     def copy(self):
#         return Block(self.key, self.states)
#
#
# class Partition:
#     def __init__(self, key_state_pairs):
#         self.blocks = {}
#         for i in range(0, len(key_state_pairs)):
#             self.blocks[i] = key_state_pairs[i]
#
#     def __getitem__(self, item):
#         return self.blocks[item]
#
#     def copy(self):
#         return Partition([(self.keys[i], self.states[i]) for i in range(0, len(self.keys))])
#
#     def count(self):
#         return len(self.blocks.keys())
#
#     def remove(self, i):
#         self.states[i] = None
#         self.keys[i] = None
#
#     def add_block(self):
#         pass
#
#     def merge(self, i, j):
#         blocks = self.blocks.copy()
#         block_i = blocks.pop(i)
#         block_j = blocks.pop(j)
#         merged_states = list(set(block_i.states.copy()).union(set(block_j.states.copy())))
#         new_key = repr({s.key for s in merged_states})
#         new_block = Block(new_key, merged_states)
#         new_blocks = list(blocks.values())
#         new_blocks.append(new_block)
#         new_key_state_pairs = [(b.key, b.states) for b in new_blocks]
#         return Partition(new_key_state_pairs)
#
#
# class State:
#     def __init__(self, key, accept=False, start=False):
#         self.key = key
#         self.neighbors = {}
#         self.accept = accept
#         self.start = start
#
#     def transition(self, symbol):
#         if symbol in self.neighbors.keys():
#             return self.neighbors[symbol]
#         else:
#             return self
#
#     def add_neighbor(self, symbol):
#         self.neighbors[symbol] = State(self.key + symbol)
#         return self.neighbors[symbol]
#
#     def traverse(self, seen_states):
#         seen_states.add(self)
#         for child in self.neighbors.values():
#             if child not in seen_states:
#                 seen_states = self.traverse(child)
#         return seen_states
#
#     def is_leaf(self):
#         if len(self.neighbors) is 0:
#             return True
#         return False
#
#
# class DFA:
#     def __init__(self, blocks):
#         self.keys = {}
#         self.states = {}
#         self.accept_states = {}
#         for i in range(0, len(blocks)):
#             block = blocks[i]
#             new_state = State(block.key)
#             for state in block.states:
#                 if state.start:
#                     self.start_state = new_state
#                 if state.accept:
#                     self.accept_states[i] = new_state
#             self.states[i] = new_state
#
#     def __getitem__(self, item):
#         current_state = self.start_state
#         for symbol in item:
#             current_state = current_state.transition(symbol)
#         if current_state.accept:
#             return 1
#         else:
#             return -1
#
#     def make_singleton_blocks(self):
#         blocks = []
#         for state in self.states.values():
#             blocks.append(Block(state.key, [state]))
#         return Partition(blocks)
#
#
#
# class PTA(DFA):
#     def __init__(self, s_plus, alphabet):
#         self.start = State('', start=True)
#         self.states = []
#         self.alphabet = alphabet
#         self.state_keys = []
#         for s in s_plus:
#             self.add_string(s)
#         blocks = [Block(state.key, [state]) for state in list(self.states)]
#         DFA.__init__(self, blocks)
#
#     # def __getitem__(self, item):
#     #     current_state = self.start
#     #     for symbol in item:
#     #         current_state = current_state.transition(symbol)
#     #     if current_state.accept:
#     #         return 1
#     #     else:
#     #         return -1
#
#     def add_string(self, s):
#         current_state = self.start
#         self.states.append(current_state)
#         for c in s:
#             next_state = current_state.transition(c)
#             if next_state is current_state:
#                 current_state = current_state.add_neighbor(c)
#                 self.states.append(current_state)
#             else:
#                 current_state = next_state
#         current_state.accept = True
#
#     # def count(self):
#     #     return len(self.start.traverse([self.start]))
#
#
#     # returns a Dictionary that maps an
#     # number i to a tuple containing the state key and state
#     def single_partition(self):
#         key_state_pairs = [(key, {self[key]}) for key in self.state_keys]
#         return Partition(key_state_pairs)











