n = int(input())
A = []

for i in range(n):
    v = [int (j) for j in input().split()]
    A.append(v)

def Job_i(i, j):
    job = A[i][j]
    for y in range(len(A)):
        if (y != i):
            k = A[y].index(min(A[y]))
            if (k != j):
                job = job + A[y][k]
            else:
                b = A[y].copy()
                b[k] = max(b)
                job = job + min(b)
    return job

time = 0
next = []
for i in range(len(A)):
    time_0 = []
    job_0 = []
    for j in range(len(A)):
        time_0.append(A[i][j])
        job_0.append(Job_i(i, j))

    for k in next:
        job_0[k] = max(job_0)
    CD = min(job_0)
    next.append(job_0.index(CD))
    time = time + time_0[job_0.index(CD)]

print(time)