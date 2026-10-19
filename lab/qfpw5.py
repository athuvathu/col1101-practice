from typing import Any, Callable, Iterable, List, NamedTuple, Optional, Tuple
EMPTY = None # the empty list, and the empty value of a level’s line
 
class Cell(NamedTuple): # one immutable linked-list cell 
    customer: Any 
    rest: Any # the cells behind this one 

class PQ(NamedTuple): # the whole queue: one line per level, plus a counter.
#The empty queue is the constant PQ(EMPTY, EMPTY, EMPTY, 0). 
    q1: Any 
    q2: Any 
    q3: Any 
    count: Any
 
def is_empty(pq): # True iff pq.count == 0 
    return pq.count == 0 

def size(pq): # return pq.count directly (do not count cells) 
    return pq.count

def move(q):
    front = q[0]
    back = q[1]
    if(back==EMPTY): return (front, EMPTY)
    nn = Cell(back.customer, front)
    return move((nn, back.rest))

def _resolve(pq, level=1):
    if(level>3): return pq
    
    if(level==1):
        if(pq.q1 == None or pq.q1[0] != None): return _resolve(pq, level+1)
        return _resolve(PQ(move(pq.q1), pq.q2, pq.q3, pq.count), level+1)
    if(level==2):
        if(pq.q2 == None or pq.q2[0] != None): return _resolve(pq, level+1)
        return _resolve(PQ(pq.q1, move(pq.q2), pq.q3, pq.count), level+1)
    if(level==3):
        if(pq.q3 == None or pq.q3[0] != None): return _resolve(pq, level+1)
        return _resolve(PQ(pq.q1, pq.q2, move(pq.q3), pq.count), level+1)

def insert(pq, customer, level): 
    # new PQ with customer at the back of level’s line, count one larger; 
    # pq is unchanged and the two untouched levels are shared, not rebuilt 
    if(level==1):
        if(pq.q1==None):
            return PQ((Cell(customer, None), None), pq.q2, pq.q3, pq.count+1)
        nn = Cell(customer, pq.q1[1])
        nq1 = (pq.q1[0], nn)
        return _resolve(PQ(nq1, pq.q2, pq.q3, pq.count+1))
    if(level==2):
        if(pq.q2==None):
            return PQ(pq.q1, (Cell(customer, None), None), pq.q3, pq.count+1)
        nn = Cell(customer, pq.q2[1])
        nq2 = (pq.q2[0], nn)
        return _resolve(PQ(pq.q1, nq2, pq.q3, pq.count+1))
    if(level==3):
        if(pq.q3==None):
            return PQ(pq.q1, pq.q2, (Cell(customer, None), None), pq.count+1)
        nn = Cell(customer, pq.q3[1])
        nq3 = (pq.q3[0], nn)
        return _resolve(PQ(pq.q1, pq.q2, nq3, pq.count+1))

def peek(pq): 
    # front customer of the lowest-numbered non-empty level, else-1 
    if(pq.q1 != None and pq.q1[0] != None):
        return pq.q1[0].customer
    if(pq.q2 != None and pq.q2[0] != None):
        return pq.q2[0].customer
    if(pq.q3 != None and pq.q3[0] != None):
        return pq.q3[0].customer
    return -1

def extract(pq): 
    # (customer, new_pq) for that customer (count one smaller), or (-1, pq ) 
    # when empty; pq is unchanged 
    if(pq.q1 != None and pq.q1[0] != None):
        res1 = pq.q1[0].customer
        nq1 = (pq.q1[0].rest, pq.q1[1])
        npq = PQ(nq1, pq.q2, pq.q3, pq.count-1)
        return (res1, _resolve(npq))
    if(pq.q2 != None and pq.q2[0] != None):
        res1 = pq.q2[0].customer
        nq2 = (pq.q2[0].rest, pq.q2[1])
        npq = PQ(pq.q1, nq2, pq.q3, pq.count-1)
        return (res1, _resolve(npq))
    if(pq.q3 != None and pq.q3[0] != None):
        res1 = pq.q3[0].customer
        nq3 = (pq.q3[0].rest, pq.q3[1])
        npq = PQ(pq.q1, pq.q2, nq3, pq.count-1)
        return (res1, _resolve(npq))
    return (-1, pq)

def to_list(pq): 
    # (customer, level) pairs in serve order (level 1, then 2, then 3); [] when empty
    if(pq.q1 != EMPTY and pq.q1[0] != EMPTY):
        e, npq = extract(pq)
        return [(e, 1)] + to_list(npq)
    if(pq.q2 != EMPTY and pq.q2[0] != EMPTY):
        e, npq = extract(pq)
        return [(e, 2)] + to_list(npq)
    if(pq.q3 != EMPTY and pq.q3[0] != EMPTY):
        e, npq = extract(pq)
        return [(e, 3)] + to_list(npq)
    return []

def reduce(function, iterable, initial, index = 0): 
    # fold: start from initial, apply function(running, item) left to right, 
    # return the final result (initial on empty). Written with recursion, no loop. 
    if(len(iterable)==index): return initial
    return reduce(function, iterable, function(iterable[index], initial), index+1)

def from_pairs(pairs): 
    # build a PQ by insert-ing each (customer, level) via reduce above, 
    # starting from PQ(EMPTY, EMPTY, EMPTY, 0); 
    # from_pairs(to_list(pq)) rebuilds an equivalent queue 
    def add_pair(pair, pq):
        return insert(pq, pair[0], pair[1])
    return reduce(add_pair, pairs, PQ(EMPTY, EMPTY, EMPTY, 0))

def run(state, operation): 
    # apply one operation; return (state, output). state is a new PQ whenever 
    # it changes, and the one passed in is left untouched. 
    if(operation[0]==1):
        return (insert(state, operation[1], operation[2]), EMPTY) 
    if(operation[0]==2):
        return (state, peek(state))
    if(operation[0]==3):
        out, ns = extract(state)
        return (ns, out)
    if(operation[0]==4):
        return (state, size(state))
    
    
    
    
    
    