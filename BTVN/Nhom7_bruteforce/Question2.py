def Maximum3Prod(a):
	n = len(a)
	p = 1
	for i in range(n-2):
		for j in range(i+1,n-1):
			for k in range(j+1,n):
				temp = a[i]*a[j]*a[k]
				if p < temp:
					p = temp*1
	return p
a = list(map(int,input().strip().split()))
print(Maximum3Prod(a))