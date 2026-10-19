from typing import List, Optional, Tuple 
NUM_LEVELS = 3 

class Node: 
    def __init__(self, customer, level, next_node=None): 
        self.customer = customer # customer ID 
        self.level = level # 1, 2, or 3 
        self.next = next_node # next node in the same level, or None
        
class PriorityQueue: 
    def __init__(self): 
        # heads[L-1], tails[L-1]: front / back node of level L (None if None) 
        # count: total requests waiting across all levels 
        self.heads = [Node(None, 1), Node(None, 2), Node(None, 3)]
        self.tails = self.heads.copy()
        self.count = 0
    def is_None(self): # True iff count == 0 
        return self.count == 0 
    def size(self): # return count directly 
        return self.count 
    def insert(self, customer, level): 
        # append a new node at the back of level’s chain; count += 1 
        nn = Node(customer, level)
        self.tails[level-1].next = nn
        self.tails[level-1] = nn
        self.count += 1
    def peek(self): 
        # front customer of the lowest-numbered non-None level, else-1 
        for i in range(3):
            if(self.heads[i] != self.tails[i]): return self.heads[i].next.customer
        return -1
    def extract(self): 
        # remove and return that customer (count-= 1), else-1 
        for i in range(3):
            if(self.heads[i] != self.tails[i]): 
                self.heads[i] = self.heads[i].next
                self.count -= 1
                return self.heads[i].customer
        return -1
    def to_list(self): 
        # every waiting request as (customer, level) pairs in serve order: 
        # all of level 1 front-to-back, then level 2, then level 3; 
        # the chains are left unchanged. Returns [] when Empty. 
        res = []
        ch = self.heads
        for i in range(3):
            if(ch[i].next == None): continue
            ch[i] = ch[i].next
            res.append(ch[i].customer)
        return res

def run(state, operation): 
   # apply one operation; return (state, output) where output is the integer 
   # the op appends or None. The returned state is the same object as state.        
    c = operation[0]
    if(c==1):
        state.insert(operation[1], operation[2])
        return (state, None)
    if(c==2):
        return (state, state.peek())
    if(c==3):
        res = state.extract()
        return (state, res)
    if(c==4):
        return (state, state.size())
    
    
    
    