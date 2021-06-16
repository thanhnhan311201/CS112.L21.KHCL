def TongUocSo(n):
	if n <= 2:
		return n-1
	s = 1
	for i in range(2,n//2+1):
		if n%i == 0:
			s+=i
	return s

l,r = list(map(int,input().strip().split()))
count = 0
for i in range(l,r+1):
	if TongUocSo(i) > i:
		count += 1
print(count)