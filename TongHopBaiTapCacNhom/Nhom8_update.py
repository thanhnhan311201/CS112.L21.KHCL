from collections import deque
class Node:
    def __init__(self, n):
        self.person = -1
        self.i = None          #job number i
        self. worker = [0]*n       #worker[i] = 1 mean task i has been allocated
        self.cost = 0           #giá trị yêu cầu đề bài
        self.lb = 0

    def Copy(self, e):
        e.person = self.person
        e.i = self.i
        e.worker = self.worker.copy()
        e.cost = self.cost
        e.lb = self.lb

def calculateLb(e, n, job, J):
    minsum = 0
    for i in range(J+1,n):
        minc = 999999
        for j in range(n):
            if e.worker[j] == 0 and job[i][j] <minc: # Tìm giá trị nhỏ nhất mỗi hàng ko gồm worker[j]
                minc = job[i][j]
        minsum += minc
    e.lb = e.cost + minsum

def bfs(job, n):
    e1 =Node(n)
    qu = []
    while e1.person < n-1:
        i = e1.person + 1
        for j in range(n): # với person[i] tính lb ở job[j]
            e = Node(n)
            e1.Copy(e)
            e.person = i
            if e.worker[j] == 1:
                continue
            e.worker[j] = 1
            e.cost += job[i][j]
            e.i = j
            calculateLb(e,n,job, i)
            qu.append(e)

        e = qu[0]
        index = 0
        for q in range(1,len(qu)): # chọn lb nhỏ nhất
            e2 = qu[q]
            if e2.lb < e.lb:
                e2.Copy(e)
                index = q
        qu.pop(index)

        e.Copy(e1) # gắn e1 = e
    print(e1.cost)


if __name__ == '__main__':
    n = int(input())
    Job = []
    for i in range(n):
        Job.append(list(map(int, input().split()[:n])))
    bfs(Job, n)
"""
tham khảo: https://www.youtube.com/watch?v=ME8Rmp3S2O8&t=1124s
https://www.programmersought.com/article/27445503876/
"""


