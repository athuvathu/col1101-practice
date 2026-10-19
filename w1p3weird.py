def polynomial_add(l0, l1):
    if(len(l0)>len(l1)): l0, l1 = l1, l0
    while(len(l0)<len(l1)): l0.append(0)
    answer = []
    for i in range(len(l0)):
        answer.append(l0[i]+l1[i])
    return answer

def polynomial_sub(l0, l1):
    while(len(l0)<len(l1)): l0.append(0)
    while(len(l0)>len(l1)): l1.append(0)
    answer = []
    for i in range(len(l0)):
        answer.append(l0[i]-l1[i])
    return answer

def polynomial_multiply_simple(p, q):
    m = len(p)-1
    n = len(q)-1
    res = []
    for i in range(m+n+1):
        c = 0
        for j in range(max(0, i-n), min(i, m)+1):
            c += p[j]*q[i-j]
        res.append(c)
    while(len(res)>1 and res[len(res)-1]==0): res.pop()
    return res

def polynomial_multiply_recursive(p, q):
    if(len(q)>len(p)): p,q = q,p
    if(len(q)==0): return [0]
    if(len(p)==1): 
        if(p[0]*q[0]): return [p[0]*q[0]]
        else: return [0]
    n = len(p)
    q = q.copy()
    while(len(q)<n): q.append(0)
    p0 = p[0:n//2]
    p1 = p[n//2:n]
    q0 = q[0:n//2]
    q1 = q[n//2:n]

    res1 = polynomial_multiply_recursive(p0, q0)
    res2 = polynomial_multiply_recursive(p1, q1)
    res3 = polynomial_multiply_recursive(polynomial_add(p0, p1), polynomial_add(q0, q1))
    res3 = polynomial_sub(res3, res1)
    res3 = polynomial_sub(res3, res2)
    res3 = ([0]*(n//2)) + res3
    res2 = ([0]*n) + res2

    while(len(res1)<len(res2)): res1.append(0)
    while(len(res3)<len(res2)): res3.append(0)

    res = polynomial_add(res1, res2)
    res = polynomial_add(res, res3)
    #while(len(res)>1 and res[len(res)-1]==0): res.pop()
    while(len(res).bit_count()>1 or len(res)==0): res.append(0)
    return res