# -*- coding: utf-8 -*-
"""BTVN_Nhom9_BranchAndBound.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QyTFF6_mu_RAftJbEhCjXZXJ7cgYsmAD
"""

import heapq


min_ans=10**18

def CostFunction (ID,job,n):
    cost=0
    available =[1]*n

    for i in range(ID+1,n):
        minx=10**18
        minIndex=-1

        for j in range(n):
            if job[j]==0 and available[i] and matrixCost[i][j]<minx:
                minIndex=j
                minx=matrixCost[i][j]
        cost+= minx
        available[minIndex]=0
    return cost


                                                                                                                                                                           
def BranchAndBound(n):
    priority_queue =[]
    heapq.heappush(priority_queue,(0,-1,[0]*n,0))

   
    while len(priority_queue):

        node=heapq.heappop(priority_queue)

        ID=node[1]+1

        if ID==n:
            return node[3]
        for j in range(n):
            if node[2][j]==0: # chưa phân công
                job=node[2].copy()
                job[j]=1
                temp = (node[0]+matrixCost[ID][j]    ,ID,   job,   node[0]+matrixCost[ID][j]+CostFunction(ID,job,n))
                heapq.heappush(priority_queue,temp)
        


n=int(input())

'''
for _ in range(n):
    table.append([int(x) for x in input().split()])
'''
matrixCost= [[9, 2, 7, 8]
        ,[6, 4, 3, 7]
        ,[5, 8, 1, 8]
        ,[7, 6, 9, 4]]

print(BranchAndBound(n))