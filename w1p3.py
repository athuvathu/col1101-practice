def polynomial_add(l0, l1):
    answer = []
    for i in range(len(l0)):
        answer.append(l0[i]+l1[i])
    return answer

def polynomial_sub(l0, l1):
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
    return res

def polynomial_multiply_recursive(p, q):
    if(len(p)==0): return [0]
    if(len(p)==1): return [p[0]*q[0]]
    n = len(p)
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
    while(len(res).bit_count()>1): res.append(0)
    return res

print(polynomial_multiply_recursive([-3, 2, 1, 0], [1, -1, 0, 0]))
print(polynomial_multiply_simple([-3, 2, 1, 0], [1, -1, 0, 0]))
