
def merge2(a, b):
    res = []
    n1 = len(a)
    n2 = len(b)
    
    i = 0
    j = 0
    while(i<n1 and j<n2):
        if(a[i]<b[j]):
            res.append(a[i])
            i+=1
        else:
            res.append(b[j])
            j+=1
    while(i<n1):
        res.append(a[i])
        i += 1
    while(j<n2):
        res.append(b[j])
        j += 1
        
    return res

def merge_div(lsts):
    n = len(lsts)
    if(n==1): return lsts[0]
    if(n==0): return []
    m = n//2
    g1 = lsts[0:m]
    g2 = lsts[m:n]
    
    return merge2(merge_div(g1), merge_div(g2))

def merge_sorted_lists(k, values):
    """
    Parameters
    ----------
    k : int
        Number of sorted lists.

    values : List[int]
        Concatenation of the k sorted lists.
    Returns
    -------
    List[int]
        A single sorted list containing all elements.
    """
    res = []
    n = len(values)
    for i in range(k):
        mew = []
        for j in range(n//k):
            mew.append(values[i*(n//k)+j])
        res.append(mew)
    
    return merge_div(res)
    
    
    
print(merge_sorted_lists(3, [2,3,1,4,6,7]))
    
    