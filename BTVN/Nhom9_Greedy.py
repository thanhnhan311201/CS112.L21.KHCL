# Câu hỏi của nhóm 10: Khi dùng hướng tiếp cận tham lam, làm sao để xác định được cấu trúc con tối ưu cho bài toán?
import numpy as np
n = int(input())
value = list(map(int,input().strip().split()))
weight = list(map(int,input().strip().split()))
limited_weight = int(input())

count_value = 0
ratio = (np.array(value)/np.array(weight))
ratio = sorted(range(n), key=lambda k: ratio[k])
for i in range(n-1,-1,-1):
	index = ratio[i]
	limited_weight += -weight[index]
	if limited_weight < 0:
		break
	count_value -= -value[index]
print(count_value)