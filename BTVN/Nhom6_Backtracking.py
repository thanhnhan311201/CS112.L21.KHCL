n = int(input())
a = list(map(int,input().strip().split()))
explored_set = []
def PrintOut(x):
  for i in range(n):
    if x[i] == 1:
      print(a[i],end=" ")
  print()
def DFS(x,n):
  if x not in explored_set:
    explored_set.append(x)
    temp = x.copy()
    zero_pos = [i for i in range(n) if x[i]==0]
    for i in zero_pos:
      temp[i] = 1
      DFS(temp,n)
      temp = x.copy()
def main():
  if n < 2:
    print('False')
  else:
    for i in range(n-1):
      x = [0]*len(a)
      x[i],x[i+1] = 1, 1
      DFS(x,n)
    for i in explored_set:
      PrintOut(i)
main()