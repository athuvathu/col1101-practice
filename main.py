def better_copy(A):
    A1 = A.copy()
    for i in range(len(A)):
        A1[i] = A[i].copy()
    return A1

def rswap(A, i, j):
    A[i], A[j] = A[j], A[i]

def rmul(A, i, k):
    for j in range(len(A[i])):
        A[i][j] = k*A[i][j]

def rcomb(A, i1, i2, k):
    #ri1 += k*ri2
    for j in range(len(A[i1])):
        A[i1][j] += k*A[i2][j]

def resolve_column(A, j, I):
    empty = True
    for i in range(j, len(A)):
        if(A[i][j]):
            empty = False
            rswap(A, j, i)
            rswap(I, j, i)

    if(empty): return -1
    rmul(I, j, 1/(A[j][j]))
    rmul(A, j, 1/(A[j][j]))
    for i in range(len(A)):
        if(i==j): continue
        rcomb(I, i, j, -A[i][j])
        rcomb(A, i, j, -A[i][j])


def type_check(A):
    good = 1
    if(type(A)!=list): good = 0
    for e in A:
        if(type(e)!=list): good = 0
        for n in e:
            if(type(n)!=float and type(n)!=int): good = 0
    return good

def val_check(A):
    n = len(A)
    good = 1
    for r in A:
        if(len(r)!=n): good = 0
    return good


def matrix_inverse(A):
    
    if(not type_check(A)): raise TypeError("Not a list of list of nums")
    if(not val_check(A)): raise ValueError("Not a square matrix")
    
    
    A1 = better_copy(A)
    n = len(A1)
    I = []
    for i in range(n):
        c = [0]*n
        c[i] = 1
        I.append(c)
        
    for j in range(n):
        if(resolve_column(A1, j, I)==-1):
            raise ValueError("Non-invertible")
    return I

matrix_inverse([[2, 1], [1, 3]])