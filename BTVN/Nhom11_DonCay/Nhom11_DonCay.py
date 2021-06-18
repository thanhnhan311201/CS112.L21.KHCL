from collections import deque
def initialize(n, a, L, R):
	S = []
	for i in range(1,n+1):
		L[i] = i
		while not(len(S) == 0) and S[len(S)-1] > i - a[i]:
			L[i] = min(L[i], L[S[len(S)-1]])
			S.pop()
		S.append(i)
	S.clear()
	for i in range(n, 0, -1):
		R[i] = i
		while not(len(S) == 0) and S[len(S)-1] < i + a[i]:
			R[i] = max(R[i], R[S[len(S)-1]])
			S.pop()
		S.append(i)
		
def solve(n, a, L, R, dp, trace):
	for i in range(1,n+1):
		dp[i] = i
		trace[i] = -i
		S = []
	for i in range(1, n+1):
		if dp[i] > dp[L[i]-1] + 1:
			dp[i] = dp[L[i]-1] + 1
			trace[i] = -L[i]
		while not(len(S) == 0) and R[S[len(S)-1]] < i:
			S.pop()

		if len(S)  and dp[i] > dp[S[-1]-1] + 1:
			dp[i] = dp[S[-1] -1] + 1
			trace[i] = S[-1]

		if len(S) == 0 or dp[S[len(S)-1]-1] > dp[i - 1]:
			S.append(i)
	print(dp[n])

	i = n
	while i :
		if trace[i] < 0:
			print(-i, end=' ')
		else:
			print(trace[i], end=' ')
		i = abs(trace[i]) - 1

def main():
	n = int(input())
	L = [i for i in range(n+1)]
	dp = [i for i in range(n+1)]
	R = [i for i in range(n+1)]
	trace = [0] * (n+1)
	a = [0] + [int(x) for x in input().split()]
	initialize(n, a, L, R)
	solve(n, a, L, R, dp, trace)
		
if __name__ == '__main__':
	main()	