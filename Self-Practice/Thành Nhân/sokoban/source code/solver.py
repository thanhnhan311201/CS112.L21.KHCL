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
    beginBox = PosOfBoxes(gameState) #l???y v??? tr?? c???a nh???ng c??i box
    beginPlayer = PosOfPlayer(gameState) #l???y v??? tr?? c???a nh??n v???t

    startState = (beginPlayer, beginBox) # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
    frontier = collections.deque([[startState]]) # store states
    actions = collections.deque([[0]]) # store actions
    exploredSet = set()
    temp = []
    ### Implement breadthFirstSearch here

    while frontier:
        node = frontier.popleft() #l???y v??? tr?? hi???n t???i c???a nh??n v???t v?? box
        node_action = actions.popleft() #l???y h??nh ?????ng hi???n t???i c???a nh??n v???t
        if isEndState(node[-1][-1]): #ki???m tra c??c box ???? v?? goal ch??a, n???u v?? r???i th?? k???t th??c game, n???u ch??a v?? th?? ti???p t???c game
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet: #ki???m tra tr???ng th??i c???a nh??n v???t ???? ???????c duy???t hay ch??a
            exploredSet.add(node[-1]) #n???u ch??a duy???t th?? th??m v?? exploreSet
            for action in legalActions(node[-1][0], node[-1][1]): #l???y ra t???ng tr???ng th??i h???p l??? ????? duy???t
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) #c???p nh???p l???i v??? tr?? m???i c???a nh???t v???t v?? c???a th??ng theo v??? tr?? h???p l??? m???i
                if isFailed(newPosBox): #ki???m tra v??? tr?? m???i c???a th??ng c?? h???p l??? hay kh??ng
                    continue #n???u kh??ng h???p l??? th?? b??? qua v??? tr?? m???i c???a th??ng
                print(frontier)
                frontier.append(node + [(newPosPlayer, newPosBox)]) #n???u v??? tr?? m???i c???a th??ng h???p l??? th?? th??m v??? tr?? m???i c???a nh??n v???t v?? th??ng v??o frontier
                actions.append(node_action + [action[-1]]) #n???u v??? tr?? m???i c???a th??ng h???p l??? th?? th??m h??nh ?????ng ti???p theo c???a nh??n v???t v??o actions
    return temp
    
def cost(actions):
    """A cost function"""
    return len([x for x in actions if x.islower()])

def uniformCostSearch(gameState):
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState) #l???y v??? tr?? c???a nh???ng c??i th??ng
    beginPlayer = PosOfPlayer(gameState) #l???y v??? tr?? c???a nh??n v???t

    startState = (beginPlayer, beginBox)
    frontier = PriorityQueue() 
    frontier.push([startState], 0) #l??u tr??? v??? tr?? c???a nh??n v???t
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0) #l??u tr??? tr???ng th??i c???a nh??n v???t
    temp = []
    ### Implement uniform cost search here

    while frontier:
        node = frontier.pop() #l???y v??? tr?? hi???n t???i c???a nh??n v???t v?? th??ng
        node_action = actions.pop() #l???y h??nh ?????ng hi???n t???i c???a nh??n v???t

        if isEndState(node[-1][-1]): #ki???m tra c??c box ???? v?? goal ch??a, n???u v?? r???i th?? k???t th??c game, n???u ch??a v?? th?? ti???p t???c game
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet: #ki???m tra tr???ng th??i c???a nh??n v???t ???? ???????c duy???t hay ch??a
            exploredSet.add(node[-1]) #n???u ch??a duy???t th?? th??m v?? exploreSet
            for action in legalActions(node[-1][0], node[-1][1]): #l???y ra t???ng tr???ng th??i h???p l??? ????? duy???t
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) #c???p nh???p l???i v??? tr?? m???i c???a nh???t v???t v?? c???a th??ng theo v??? tr?? h???p l??? m???i
                if isFailed(newPosBox): #ki???m tra v??? tr?? m???i c???a th??ng c?? h???p l??? hay kh??ng
                    continue #n???u kh??ng h???p l??? th?? b??? qua v??? tr?? m???i c???a th??ng
                new_action = node_action + [action[-1]]
                frontier.push(node + [(newPosPlayer, newPosBox)],cost(new_action[1:])) #n???u v??? tr?? m???i c???a th??ng h???p l??? th?? th??m v??? tr?? m???i c???a nh??n v???t, th??ng v?? s??? b?????c ??i c???a nh??n v???t t??? tr???ng th??i ban ?????u t???i tr???ng th??i ti???p theo v??o frontier
                actions.push(node_action + [action[-1]],cost(new_action[1:])) #n???u v??? tr?? m???i c???a th??ng h???p l??? th?? th??m h??nh ?????ng ti???p theo v?? s??? b?????c ??i c???a nh??n v???t t??? tr???ng th??i ban ?????u t???i tr???ng th??i ti???p theo v??o actions
    print(len(temp))
    return temp

def manDistance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2) #t??nh kho???ng c??ch manhattan

def euclidDistance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) #t??nh kho???ng c??ch euclid

def mat_heuristic_1s(posBox):
    dist_cost = 0
    for x1, y1 in posBox:
        min_dist = 2**31
        for x2, y2 in posGoals:
            new_dist = manDistance(x1, y1, x2, y2) #t??nh kho???ng c??ch manhattan t??? box t???i goal g???n nh???t
            if new_dist < min_dist:
                min_dist = new_dist
        dist_cost += min_dist

    return dist_cost * (1.0 + 1/1000) #tr??? v??? t???ng kho???ng c??ch manhattans c???a m???i box t???i goal g???n nh???t

def mat_heuristic_2s(posBox, posPlayer):
    dist_cost = 0
    for x1, y1 in posBox:
        min_dist = 2**31
        for x2, y2 in posGoals:
            new_dist = manDistance(x1, y1, x2, y2) #t??nh kho???ng c??ch manhattan t??? box t???i goal g???n nh???t
            if new_dist < min_dist:
                min_dist = new_dist
        dist_cost += min_dist

    (a, b) = posPlayer
    for x, y in posBox:
        dist_min = 2**31
        dist_new = manDistance(a, b, x, y) #t??nh kho???ng c??ch manhattan t??? nh??n v???t t???i goal g???n nh???t
        if dist_new < dist_min:
            dist_min = dist_new
    dist_cost += dist_new

    return dist_cost * (1.0 + 1/1000) #tr??? v??? t???ng kho???ng c??ch manhattan c???a m???i box t???i goal g???n nh???t v?? kho???ng c??ch t??? nh??n v???t t???i box g???n nh???t

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
        dist_cost += min_dist #t??nh kho???ng c??ch manhattan c???a m???i box t???i goal g???n nh???t nh??ng n?? c??c tr?????ng h???p nhi???u box t??m t???i chung goal

    (a, b) = posPlayer
    for x, y in posBox:
        dist_min = 2**31
        dist_new = manDistance(a, b, x, y) #t??nh kho???ng c??ch manhattan c???a nh??n v???t t???i box g???n nh???t
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
            new_dist = euclidDistance(x1, y1, x2, y2) #t??nh kho???ng c??ch euclid c???a m???i box t???i goal g???n nh???t
            if new_dist < min_dist:
                min_dist = new_dist
        dist_cost += min_dist

    return dist_cost * (1.0 + 1/1000) #tr??? v??? t???ng kho???ng c??ch euclid c???a m???i box t???i goal g???n nh???t

def euc_heuristic_2s(posBox, posPlayer):
    dist_cost = 0
    for x1, y1 in posBox:
        min_dist = 2**31
        for x2, y2 in posGoals:
            new_dist = euclidDistance(x1, y1, x2, y2) #t??nh kho???ng c??ch euclid c???a m???i box t???i goal g???n nh???t
            if new_dist < min_dist:
                min_dist = new_dist
        dist_cost += min_dist

    (a, b) = posPlayer
    for x, y in posBox:
        dist_min = 2**31
        dist_new = manDistance(a, b, x, y) #t??nh kho???ng c??ch euclid c???a nh??n v???t t???i box g???n nh???t
        if dist_new < dist_min:
            dist_min = dist_new
    dist_cost += dist_new

    return dist_cost * (1.0 + 1/1000) #tr??? v??? t???ng kho???ng c??ch euclid c???a m???i box t???i goal g???n nh???t v?? kho???ng c??ch nh??n v???t t???i box g???n nh???t

def greedySearch(gameState):
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState) #l???y v??? tr?? c???a nh???ng c??i th??ng
    beginPlayer = PosOfPlayer(gameState) #l???y v??? tr?? c???a nh??n v???t

    startState = (beginPlayer, beginBox)
    frontier = PriorityQueue() 
    frontier.push([startState], 0) #l??u tr??? v??? tr?? c???a nh??n v???t
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0) #l??u tr??? tr???ng th??i c???a nh??n v???t
    temp = []
    ### Implement uniform cost search here

    while frontier:
        node = frontier.pop() #l???y v??? tr?? hi???n t???i c???a nh??n v???t v?? th??ng
        node_action = actions.pop() #l???y h??nh ?????ng hi???n t???i c???a nh??n v???t

        if isEndState(node[-1][-1]): #ki???m tra c??c box ???? v?? goal ch??a, n???u v?? r???i th?? k???t th??c game, n???u ch??a v?? th?? ti???p t???c game
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet: #ki???m tra tr???ng th??i c???a nh??n v???t ???? ???????c duy???t hay ch??a
            exploredSet.add(node[-1]) #n???u ch??a duy???t th?? th??m v?? exploreSet
            for action in legalActions(node[-1][0], node[-1][1]): #l???y ra t???ng tr???ng th??i h???p l??? ????? duy???t
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) #c???p nh???p l???i v??? tr?? m???i c???a nh???t v???t v?? c???a th??ng theo v??? tr?? h???p l??? m???i
                if isFailed(newPosBox): #ki???m tra v??? tr?? m???i c???a th??ng c?? h???p l??? hay kh??ng
                    continue #n???u kh??ng h???p l??? th?? b??? qua v??? tr?? m???i c???a th??ng
                frontier.push(node + [(newPosPlayer, newPosBox)], mat_heuristic_1s(newPosBox)) #n???u v??? tr?? m???i c???a th??ng h???p l??? th?? th??m v??? tr?? m???i c???a nh??n v???t, th??ng v?? chi ph?? ?????c t??nh v??o frontier
                actions.push(node_action + [action[-1]], mat_heuristic_1s(newPosBox)) #n???u v??? tr?? m???i c???a th??ng h???p l??? th?? th??m h??nh ?????ng ti???p theo v?? chi ph?? ?????c t??nh v??o actions
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
    beginBox = PosOfBoxes(gameState) #l???y v??? tr?? c???a nh???ng c??i th??ng
    beginPlayer = PosOfPlayer(gameState) #l???y v??? tr?? c???a nh??n v???t

    startState = (beginPlayer, beginBox)
    frontier = PriorityQueue() 
    frontier.push([startState], 0) #l??u tr??? v??? tr?? c???a nh??n v???t
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0) #l??u tr??? tr???ng th??i c???a nh??n v???t
    temp = []
    ### Implement uniform cost search here

    while frontier:
        node = frontier.pop() #l???y v??? tr?? hi???n t???i c???a nh??n v???t v?? th??ng
        node_action = actions.pop() #l???y h??nh ?????ng hi???n t???i c???a nh??n v???t

        if isEndState(node[-1][-1]): #ki???m tra c??c box ???? v?? goal ch??a, n???u v?? r???i th?? k???t th??c game, n???u ch??a v?? th?? ti???p t???c game
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet: #ki???m tra tr???ng th??i c???a nh??n v???t ???? ???????c duy???t hay ch??a
            exploredSet.add(node[-1]) #n???u ch??a duy???t th?? th??m v?? exploreSet
            for action in legalActions(node[-1][0], node[-1][1]): #l???y ra t???ng tr???ng th??i h???p l??? ????? duy???t
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) #c???p nh???p l???i v??? tr?? m???i c???a nh???t v???t v?? c???a th??ng theo v??? tr?? h???p l??? m???i
                if isFailed(newPosBox): #ki???m tra v??? tr?? m???i c???a th??ng c?? h???p l??? hay kh??ng
                    continue #n???u kh??ng h???p l??? th?? b??? qua v??? tr?? m???i c???a th??ng
                new_action = node_action + [action[-1]]
                frontier.push(node + [(newPosPlayer, newPosBox)],cost(new_action[1:]) + mat_heuristic_1s(newPosBox)) #n???u v??? tr?? m???i c???a th??ng h???p l??? th?? th??m v??? tr?? m???i c???a nh??n v???t, th??ng v?? chi ph?? ?????c t??nh v??o frontier
                actions.push(node_action + [action[-1]],cost(new_action[1:]) + mat_heuristic_1s(newPosBox)) #n???u v??? tr?? m???i c???a th??ng h???p l??? th?? th??m h??nh ?????ng ti???p theo chi ph?? ?????c t??nh v??o actions
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
