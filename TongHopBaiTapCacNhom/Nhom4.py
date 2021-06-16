import heapq

table = []
min_ans = 10**18

def CostFunction(id_, n, assigned):
	cost = 0
	availabel = [1] * n

	for i in range(id_ + 1, n):
		minx = 10**18 
		minIndex = -1

		for j in range(n):
			if assigned[j] == 0 and availabel[j] and table[i][j] < minx:
				minIndex = j
				minx = table[i][j]

		cost += minx 
		availabel[minIndex] = 0

	return cost

def BranchAndBound(n):
	priority_queue = []
	heapq.heappush(priority_queue, (0, -1, [0]*n, 0))
	# 1 node luu cac gia tri:
	# node[0] = thời gian khi chọn đến công nhân node[1]
	# node[1] = chỉ số của công nhân 
	# node[2] = trạng thải bảng phân công công việc
	# node[3] = thời gian đã tiêu tốn

	while len(priority_queue):
		node = heapq.heappop(priority_queue)
		id_ = node[1] + 1
		if  id_ == n:
			print(node[3])
			return

		for j in range(n):
			if node[2][j] == 0:
				assigned = node[2].copy()
				assigned[j] = 1
				temp = (node[0] + table[id_][j], id_, assigned,\
						node[0] + table[id_][j] +\
						CostFunction(id_, n, assigned))
				heapq.heappush(priority_queue, temp)

if __name__ == '__main__':
	n = int(input())
	for _ in range(n):
		table.append([int(x) for x in input().split()])

	BranchAndBound(n)
