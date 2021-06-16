from operator import itemgetter
def Nhom1(n, c):
    JobAssignment = list()
    TotalTime = 0

    for W in range(n-1):
        store = list()
        for J in range(n):
            if J not in JobAssignment:
                Cost = c[W][J]
                temp = [J,]
                for w in range(W + 1, n):
                    min = 1000000000000000000000000000000
                    for j in range(n):
                        if j not in JobAssignment and j not in temp:
                            if c[w][j] < min:
                                min = c[w][j]
                                jdx = j
                    Cost += c[w][jdx]
                    temp.append(jdx)
                #print(J, Cost)
                store.append([J, Cost])
        store.sort(key=itemgetter(1))
        JobAssignment.append(store[0][0])

    for J in range(n):
        if J not in JobAssignment:
            JobAssignment.append(J)

    for W in range(n):
        TotalTime += c[W][JobAssignment[W]]
    print(JobAssignment)
    return TotalTime

n = int(input())
c = []
for i in range(n):
    c.append([int(j) for j in input().split()])

Nhom1(n,c)

