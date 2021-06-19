import sys
import collections
import numpy as np
import heapq
import time
import numpy as np
import math

global posWalls, posGoals
class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""
    def  __init__(self):
        self.Heap = []
        self.Count = 0
        self.len = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0

"""Load puzzles and define the rules of sokoban"""

def transferToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace('\n','') for x in layout]
    layout = [','.join(layout[i]) for i in range(len(layout))]
    layout = [x.split(',') for x in layout]
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == ' ': layout[irow][icol] = 0   # free space
            elif layout[irow][icol] == '#': layout[irow][icol] = 1 # wall
            elif layout[irow][icol] == '&': layout[irow][icol] = 2 # player
            elif layout[irow][icol] == 'B': layout[irow][icol] = 3 # box
            elif layout[irow][icol] == '.': layout[irow][icol] = 4 # goal
            elif layout[irow][icol] == 'X': layout[irow][icol] = 5 # box on goal
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)]) 

    # print(layout)
    return np.array(layout)
def transferToGameState2(layout, player_pos):
    """Transfer the layout of initial puzzle"""
    maxColsNum = max([len(x) for x in layout])
    temp = np.ones((len(layout), maxColsNum))
    for i, row in enumerate(layout):
        for j, val in enumerate(row):
            temp[i][j] = layout[i][j]

    temp[player_pos[1]][player_pos[0]] = 2
    return temp

def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0]) # e.g. (2, 2)

def PosOfBoxes(gameState):
    """Return the positions of boxes"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5))) # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))

def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1)) # e.g. like those above

def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5))) # e.g. like those above

def isEndState(posBox):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(posBox) == sorted(posGoals)

def isLegalAction(action, posPlayer, posBox):
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper(): # the move was a push
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in posBox + posWalls

def legalActions(posPlayer, posBox):
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1,0,'u','U'],[1,0,'d','D'],[0,-1,'l','L'],[0,1,'r','R']]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox: # the move was a push
            action.pop(2) # drop the little letter
        else:
            action.pop(3) # drop the upper letter
        if isLegalAction(action, posPlayer, posBox):
            legalActions.append(action)
        else: 
            continue     
    return tuple(tuple(x) for x in legalActions) # e.g. ((0, -1, 'l'), (0, 1, 'R'))

def updateState(posPlayer, posBox, action):
    """Return updated game state after an action is taken"""
    xPlayer, yPlayer = posPlayer # the previous position of player
    newPosPlayer = [xPlayer + action[0], yPlayer + action[1]] # the current position of player
    posBox = [list(x) for x in posBox]
    if action[-1].isupper(): # if pushing, update the position of box
        posBox.remove(newPosPlayer)
        posBox.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
    posBox = tuple(tuple(x) for x in posBox)
    newPosPlayer = tuple(newPosPlayer)
    return newPosPlayer, posBox

def isFailed(posBox):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [[0,1,2,3,4,5,6,7,8],
                    [2,5,8,1,4,7,0,3,6],
                    [0,1,2,3,4,5,6,7,8][::-1],
                    [2,5,8,1,4,7,0,3,6][::-1]]
    flipPattern = [[2,1,0,5,4,3,8,7,6],
                    [0,3,6,1,4,7,2,5,8],
                    [2,1,0,5,4,3,8,7,6][::-1],
                    [0,3,6,1,4,7,2,5,8][::-1]]
    allPattern = rotatePattern + flipPattern

    for box in posBox:
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1), 
                    (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1), 
                    (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls: return True
    return False

"""Implement all approcahes"""

def depthFirstSearch(gameState):
    """Implement depthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)
    startState = (beginPlayer, beginBox)
    frontier = collections.deque([[startState]])

    exploredSet = set()
    actions = [[0]]
    temp = []
    while frontier:
        node = frontier.pop()
        node_action = actions.pop()
        if isEndState(node[-1][-1]):
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])
    return temp

def breadthFirstSearch(gameState):
    """Implement breadthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState) #lấy vị trí của những cái box
    beginPlayer = PosOfPlayer(gameState) #lấy vị trí của nhân vật

    startState = (beginPlayer, beginBox) # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
    frontier = collections.deque([[startState]]) # store states
    actions = collections.deque([[0]]) # store actions
    exploredSet = set()
    temp = []
    ### Implement breadthFirstSearch here

    while frontier:
        node = frontier.popleft() #lấy vị trí hiện tại của nhân vật và box
        node_action = actions.popleft() #lấy hành động hiện tại của nhân vật
        if isEndState(node[-1][-1]): #kiểm tra các box đã vô goal chưa, nếu vô rồi thì kết thúc game, nếu chưa vô thì tiếp tục game
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet: #kiểm tra trạng thái của nhân vật đã được duyệt hay chưa
            exploredSet.add(node[-1]) #nếu chưa duyệt thì thêm vô exploreSet
            for action in legalActions(node[-1][0], node[-1][1]): #lấy ra từng trạng thái hợp lệ để duyệt
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) #cập nhập lại vị trí mới của nhật vật và của thùng theo vị trí hợp lệ mới
                if isFailed(newPosBox): #kiểm tra vị trí mới của thùng có hợp lệ hay không
                    continue #nếu không hợp lệ thì bỏ qua vị trí mới của thùng
                print(frontier)
                frontier.append(node + [(newPosPlayer, newPosBox)]) #nếu vị trí mới của thùng hợp lệ thì thêm vị trí mới của nhân vật và thùng vào frontier
                actions.append(node_action + [action[-1]]) #nếu vị trí mới của thùng hợp lệ thì thêm hành động tiếp theo của nhân vật vào actions
    return temp
    
def cost(actions):
    """A cost function"""
    return len([x for x in actions if x.islower()])

def uniformCostSearch(gameState):
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState) #lấy vị trí của những cái thùng
    beginPlayer = PosOfPlayer(gameState) #lấy vị trí của nhân vật

    startState = (beginPlayer, beginBox)
    frontier = PriorityQueue() 
    frontier.push([startState], 0) #lưu trữ vị trí của nhân vật
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0) #lưu trữ trạng thái của nhân vật
    temp = []
    ### Implement uniform cost search here

    while frontier:
        node = frontier.pop() #lấy vị trí hiện tại của nhân vật và thùng
        node_action = actions.pop() #lấy hành động hiện tại của nhân vật

        if isEndState(node[-1][-1]): #kiểm tra các box đã vô goal chưa, nếu vô rồi thì kết thúc game, nếu chưa vô thì tiếp tục game
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet: #kiểm tra trạng thái của nhân vật đã được duyệt hay chưa
            exploredSet.add(node[-1]) #nếu chưa duyệt thì thêm vô exploreSet
            for action in legalActions(node[-1][0], node[-1][1]): #lấy ra từng trạng thái hợp lệ để duyệt
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) #cập nhập lại vị trí mới của nhật vật và của thùng theo vị trí hợp lệ mới
                if isFailed(newPosBox): #kiểm tra vị trí mới của thùng có hợp lệ hay không
                    continue #nếu không hợp lệ thì bỏ qua vị trí mới của thùng
                new_action = node_action + [action[-1]]
                frontier.push(node + [(newPosPlayer, newPosBox)],cost(new_action[1:])) #nếu vị trí mới của thùng hợp lệ thì thêm vị trí mới của nhân vật, thùng và số bước đi của nhân vật từ trạng thái ban đầu tới trạng thái tiếp theo vào frontier
                actions.push(node_action + [action[-1]],cost(new_action[1:])) #nếu vị trí mới của thùng hợp lệ thì thêm hành động tiếp theo và số bước đi của nhân vật từ trạng thái ban đầu tới trạng thái tiếp theo vào actions
    print(len(temp))
    return temp

def manDistance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2) #tính khoảng cách manhattan

def euclidDistance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) #tính khoảng cách euclid

def mat_heuristic_1s(posBox):
    dist_cost = 0
    for x1, y1 in posBox:
        min_dist = 2**31
        for x2, y2 in posGoals:
            new_dist = manDistance(x1, y1, x2, y2) #tính khoảng cách manhattan từ box tới goal gần nhất
            if new_dist < min_dist:
                min_dist = new_dist
        dist_cost += min_dist

    return dist_cost * (1.0 + 1/1000) #trả về tổng khoảng cách manhattans của mỗi box tới goal gần nhất

def mat_heuristic_2s(posBox, posPlayer):
    dist_cost = 0
    for x1, y1 in posBox:
        min_dist = 2**31
        for x2, y2 in posGoals:
            new_dist = manDistance(x1, y1, x2, y2) #tính khoảng cách manhattan từ box tới goal gần nhất
            if new_dist < min_dist:
                min_dist = new_dist
        dist_cost += min_dist

    (a, b) = posPlayer
    for x, y in posBox:
        dist_min = 2**31
        dist_new = manDistance(a, b, x, y) #tính khoảng cách manhattan từ nhân vật tới goal gần nhất
        if dist_new < dist_min:
            dist_min = dist_new
    dist_cost += dist_new

    return dist_cost * (1.0 + 1/1000) #trả về tổng khoảng cách manhattan của mỗi box tới goal gần nhất và khoảng cách từ nhân vật tới box gần nhất

def mat_heuristic_3s(posBox, posPlayer):
    dist_cost = 0
    exc = []

    for x1, y1 in posBox:
        min_dist = 2**31
        for x2, y2 in posGoals:
            if len(exc) != 0:
                exc_p = exc.pop()
                if j != exc_p:
                    j = 0
                    new_dist = manDistance(x1, y1, x2, y2)
                    if new_dist < min_dist:
                        min_dist = new_dist
                        exc.append(j)
                    j += 1
            else:
                j = 0
                new_dist = manDistance(x1, y1, x2, y2)
                if new_dist < min_dist:
                    min_dist = new_dist
                    exc.append(j)
                j += 1
        dist_cost += min_dist #tính khoảng cách manhattan của mỗi box tới goal gần nhất nhưng né các trường hợp nhiều box tìm tới chung goal

    (a, b) = posPlayer
    for x, y in posBox:
        dist_min = 2**31
        dist_new = manDistance(a, b, x, y) #tính khoảng cách manhattan của nhân vật tới box gần nhất
        if dist_new < dist_min:
            dist_min = dist_new
    dist_cost += dist_new

    # for x1, y1 in posBox:
    #     m_dist = 2**31
    #     for x2, y2 in posGoals:
    #         new_dist = manDistance(x1, y1, x2, y2) 
    #         if new_dist < min_dist:
    #             m_dist = new_dist
    #     dist_cost += m_dist

    return dist_cost * (1.0 + 1/1000)

def euc_heuristic_1s(posBox):
    dist_cost = 0
    for x1, y1 in posBox:
        min_dist = 2**31
        for x2, y2 in posGoals:
            new_dist = euclidDistance(x1, y1, x2, y2) #tính khoảng cách euclid của mỗi box tới goal gần nhất
            if new_dist < min_dist:
                min_dist = new_dist
        dist_cost += min_dist

    return dist_cost * (1.0 + 1/1000) #trả về tổng khoảng cách euclid của mỗi box tới goal gần nhất

def euc_heuristic_2s(posBox, posPlayer):
    dist_cost = 0
    for x1, y1 in posBox:
        min_dist = 2**31
        for x2, y2 in posGoals:
            new_dist = euclidDistance(x1, y1, x2, y2) #tính khoảng cách euclid của mỗi box tới goal gần nhất
            if new_dist < min_dist:
                min_dist = new_dist
        dist_cost += min_dist

    (a, b) = posPlayer
    for x, y in posBox:
        dist_min = 2**31
        dist_new = manDistance(a, b, x, y) #tính khoảng cách euclid của nhân vật tới box gần nhất
        if dist_new < dist_min:
            dist_min = dist_new
    dist_cost += dist_new

    return dist_cost * (1.0 + 1/1000) #trả về tổng khoảng cách euclid của mỗi box tới goal gần nhất và khoảng cách nhân vật tới box gần nhất

def greedySearch(gameState):
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState) #lấy vị trí của những cái thùng
    beginPlayer = PosOfPlayer(gameState) #lấy vị trí của nhân vật

    startState = (beginPlayer, beginBox)
    frontier = PriorityQueue() 
    frontier.push([startState], 0) #lưu trữ vị trí của nhân vật
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0) #lưu trữ trạng thái của nhân vật
    temp = []
    ### Implement uniform cost search here

    while frontier:
        node = frontier.pop() #lấy vị trí hiện tại của nhân vật và thùng
        node_action = actions.pop() #lấy hành động hiện tại của nhân vật

        if isEndState(node[-1][-1]): #kiểm tra các box đã vô goal chưa, nếu vô rồi thì kết thúc game, nếu chưa vô thì tiếp tục game
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet: #kiểm tra trạng thái của nhân vật đã được duyệt hay chưa
            exploredSet.add(node[-1]) #nếu chưa duyệt thì thêm vô exploreSet
            for action in legalActions(node[-1][0], node[-1][1]): #lấy ra từng trạng thái hợp lệ để duyệt
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) #cập nhập lại vị trí mới của nhật vật và của thùng theo vị trí hợp lệ mới
                if isFailed(newPosBox): #kiểm tra vị trí mới của thùng có hợp lệ hay không
                    continue #nếu không hợp lệ thì bỏ qua vị trí mới của thùng
                frontier.push(node + [(newPosPlayer, newPosBox)], mat_heuristic_1s(newPosBox)) #nếu vị trí mới của thùng hợp lệ thì thêm vị trí mới của nhân vật, thùng và chi phí ước tính vào frontier
                actions.push(node_action + [action[-1]], mat_heuristic_1s(newPosBox)) #nếu vị trí mới của thùng hợp lệ thì thêm hành động tiếp theo và chi phí ước tính vào actions
                #frontier.push(node + [(newPosPlayer, newPosBox)], mat_heuristic_2s(newPosBox, newPosPlayer))
                #actions.push(node_action + [action[-1]], mat_heuristic_2s(newPosBox, newPosPlayer))
                #frontier.push(node + [(newPosPlayer, newPosBox)], mat_heuristic_3s(newPosBox, newPosPlayer))
                #actions.push(node_action + [action[-1]], mat_heuristic_3s(newPosBox, newPosPlayer))
                #frontier.push(node + [(newPosPlayer, newPosBox)], euc_heuristic_1s(newPosBox))
                #actions.push(node_action + [action[-1]], euc_heuristic_1s(newPosBox))
                #frontier.push(node + [(newPosPlayer, newPosBox)], euc_heuristic_2s(newPosBox, newPosPlayer))
                #actions.push(node_action + [action[-1]], euc_heuristic_2s(newPosBox, newPosPlayer))
    print(len(temp))
    return temp

def aStarSearch(gameState):
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState) #lấy vị trí của những cái thùng
    beginPlayer = PosOfPlayer(gameState) #lấy vị trí của nhân vật

    startState = (beginPlayer, beginBox)
    frontier = PriorityQueue() 
    frontier.push([startState], 0) #lưu trữ vị trí của nhân vật
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0) #lưu trữ trạng thái của nhân vật
    temp = []
    ### Implement uniform cost search here

    while frontier:
        node = frontier.pop() #lấy vị trí hiện tại của nhân vật và thùng
        node_action = actions.pop() #lấy hành động hiện tại của nhân vật

        if isEndState(node[-1][-1]): #kiểm tra các box đã vô goal chưa, nếu vô rồi thì kết thúc game, nếu chưa vô thì tiếp tục game
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet: #kiểm tra trạng thái của nhân vật đã được duyệt hay chưa
            exploredSet.add(node[-1]) #nếu chưa duyệt thì thêm vô exploreSet
            for action in legalActions(node[-1][0], node[-1][1]): #lấy ra từng trạng thái hợp lệ để duyệt
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) #cập nhập lại vị trí mới của nhật vật và của thùng theo vị trí hợp lệ mới
                if isFailed(newPosBox): #kiểm tra vị trí mới của thùng có hợp lệ hay không
                    continue #nếu không hợp lệ thì bỏ qua vị trí mới của thùng
                new_action = node_action + [action[-1]]
                frontier.push(node + [(newPosPlayer, newPosBox)],cost(new_action[1:]) + mat_heuristic_1s(newPosBox)) #nếu vị trí mới của thùng hợp lệ thì thêm vị trí mới của nhân vật, thùng và chi phí ước tính vào frontier
                actions.push(node_action + [action[-1]],cost(new_action[1:]) + mat_heuristic_1s(newPosBox)) #nếu vị trí mới của thùng hợp lệ thì thêm hành động tiếp theo chi phí ước tính vào actions
                #frontier.push(node + [(newPosPlayer, newPosBox)],cost(new_action[1:]) + mat_heuristic_2s(newPosBox, newPosPlayer))
                #actions.push(node_action + [action[-1]],cost(new_action[1:]) + mat_heuristic_2s(newPosBox, newPosPlayer))
                #frontier.push(node + [(newPosPlayer, newPosBox)],cost(new_action[1:]) + mat_heuristic_3s(newPosBox, newPosPlayer))
                #actions.push(node_action + [action[-1]],cost(new_action[1:]) + mat_heuristic_3s(newPosBox, newPosPlayer))
                #frontier.push(node + [(newPosPlayer, newPosBox)],cost(new_action[1:]) + euc_heuristic_1s(newPosBox))
                #actions.push(node_action + [action[-1]],cost(new_action[1:]) + euc_heuristic_1s(newPosBox))
                #frontier.push(node + [(newPosPlayer, newPosBox)],cost(new_action[1:]) + euc_heuristic_2s(newPosBox, newPosPlayer))
                #actions.push(node_action + [action[-1]],cost(new_action[1:]) + euc_heuristic_2s(newPosBox, newPosPlayer))
    print(len(temp))
    return temp

"""Read command"""
def readCommand(argv):
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokobanLevels',
                      help='level of game to play', default='level1.txt')
    parser.add_option('-m', '--method', dest='agentMethod',
                      help='research method', default='bfs')
    args = dict()
    options, _ = parser.parse_args(argv)
    with open('assets/levels/' + options.sokobanLevels,"r") as f: 
        layout = f.readlines()
    args['layout'] = layout
    args['method'] = options.agentMethod
    return args

def get_move(layout, player_pos, method):
    time_start = time.time()
    global posWalls, posGoals
    # layout, method = readCommand(sys.argv[1:]).values()
    gameState = transferToGameState2(layout, player_pos)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)
    if method == 'dfs':
        result = depthFirstSearch(gameState)
    elif method == 'bfs':
        result = breadthFirstSearch(gameState)    
    elif method == 'ucs':
        result = uniformCostSearch(gameState)
    elif method == 'gds':
        result = greedySearch(gameState)
    elif method == 'ass':
        result = aStarSearch(gameState)
    else:
        raise ValueError('Invalid method.')
    time_end=time.time()
    print('Runtime of %s: %.2f second.' %(method, time_end-time_start))
    print(result)
    return result
