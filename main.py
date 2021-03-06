### Filipescu Radu - 251
### Micul Vrajitor

from datetime import datetime
import numpy as np
from queue import PriorityQueue, Queue
from collections import defaultdict

### reading input data
DEVELOP_MODE = True

if DEVELOP_MODE:
    INPUT_FILEPATH = "input.txt"
    OUTPUT_FILEPATH = "output"
    NSOL = 2
    TIMEOUT_SEC = 8
else:
    print("Please enter input filepath:")
    INPUT_FILEPATH = input()
    print("Please enter output path:")
    OUTPUT_FILEPATH = input()
    print("Please enter the number of solutions to print:")
    NSOL = int(input())
    print("Please enter timeout (seconds):")
    TIMEOUT_SEC = int(input())

def defFactory():
    return -1
color_cost_map = defaultdict(defFactory)

input_file = open(INPUT_FILEPATH, "rt", encoding="utf-8")

input_line = input_file.readline()
while input_line != "----\n":
    input_line = input_line.split()
    color_cost_map[input_line[0]] = int(input_line[1])
    input_line = input_file.readline()

color_matrix = []

input_line = input_file.readline()
while input_line != "\n":
    input_line = input_line.split()

    row = []
    for x in input_line:
        row.append(x)

    color_matrix.append(row)
    input_line = input_file.readline()

# using numpy for faster access and manipulation
color_matrix = np.array(color_matrix)

boots_matrix = []

input_line = input_file.readline()
while input_line != "":
    input_line = input_line.split()

    row = []
    for x in input_line:
        row.append(x)

    boots_matrix.append(row)
    input_line = input_file.readline()

boots_matrix = np.array(boots_matrix)

START_POSITION = (-1, -1)
STONE_POSITION = (-1, -1)

for i in range(len(boots_matrix)):
    for j in range(len(boots_matrix[i])):
        if boots_matrix[i][j] == '*':
            START_POSITION = (i, j)
        if boots_matrix[i][j] == '@':
            STONE_POSITION = (i, j)



# defining a state of the game with default values
class State:
    def __init__(self, gotStone, position, boots):
        self.gotStone = gotStone
        self.position = position
        self.boots = boots

        # auto-increment state Id ( label )
        self.id = 0
        if (self in state_id_map):
            self.id = state_id_map[self]
        else:
            self.id = len(state_id_map) + 1
            state_id_map[self] = self.id

    def __repr__(self):
        temp = "";
        for boot in self.boots:
            temp += str(boot[0]) + ", " + str(boot[1]) + " | "

        return "\nId is " + str(self.id) + "\nposition is " + str(self.position[0]) + ", " + str(self.position[1]) + "\nstone: " + str(self.gotStone) + \
                "\nboots are: " + temp + "\n"

    def __lt__(self, other):
        return self.gotStone > other.gotStone or (self.gotStone == other.gotStone and len(self.boots) > len(other.boots))

    def __hash__(self):
        return hash((self.position, str(self.boots), self.gotStone))

    def __eq__(self, other):
        if other is None: return False
        return self.gotStone == other.gotStone and self.position[0] == other.position[0] \
               and self.position[1] == other.position[1] and bootSetsAreEqual(self.boots, other.boots)

state_id_map = defaultdict(defFactory)

def bootSetsAreEqual(boots1, boots2):
    if len(boots1) == 0 and len(boots2) == 0:
        return True

    if len(boots1) != len(boots2):
        return False

    if len(boots1) == 1:
        return boots1[0] == boots2[0]

    return (boots1[0] == boots2[0] and boots1[1] == boots2[1]) \
        or (boots1[0] == boots2[1] and boots1[1] == boots2[0])

def bootsAreOkay(boots, L, C):
    if len(boots) == 0:
        return False

    if len(boots) == 1:
        return boots[0][0] == color_matrix[L][C] and boots[0][1] < 3

    # else means that len(boots) == 2
    return (boots[0][0] == color_matrix[L][C] and boots[0][1] < 3) or \
           (boots[1][0] == color_matrix[L][C] and boots[1][1] < 3)

# return list of (adjacent_state, cost) tuples
def getPossibleMoves(currentState):
    l = currentState.position[0]
    c = currentState.position[1]

    possibleStates = []
    adjacentPositions = [(l - 1, c), (l, c + 1), (l + 1, c), (l, c - 1)]

    for p in adjacentPositions:
        L = p[0]
        C = p[1]

        # if valid position
        if L >= 0 and L < len(boots_matrix) and C >= 0 and C < len(boots_matrix[0]):
            ## these will be (kinda) common for all adjacent states
            stoneStatus = bool(boots_matrix[L][C] == '@' or currentState.gotStone)
            futureCost = color_cost_map[color_matrix[L][C]]

            # step onto next state, using currently equipped boots
            if currentState.boots[0][0] == color_matrix[L][C] and currentState.boots[0][1] < 3:
                nextBoots = [(currentState.boots[0][0], currentState.boots[0][1] + 1)]
                if len(currentState.boots) == 2 and currentState.boots[1][1] < 3:
                    nextBoots.append((currentState.boots[1][0], currentState.boots[1][1]))

                nextState = State(stoneStatus, (L, C), nextBoots)

                possibleStates.append((nextState, futureCost))

            # or step onto next state after swapping equipped boots with boots in the inventory
            if len(currentState.boots) == 2 and currentState.boots[1][0] == color_matrix[L][C] \
                and currentState.boots[1][1] < 3:

                nextBoots = [(currentState.boots[1][0], currentState.boots[1][1] + 1)]
                # if old equipped boots aren't too used
                if currentState.boots[0][1] < 3:
                    nextBoots.append((currentState.boots[0][0], currentState.boots[0][1]))

                nextState = State(stoneStatus, (L, C), nextBoots)

                possibleStates.append((nextState, futureCost + 1))

            # if we have boots on the position we are at
            if boots_matrix[l][c] not in ['0', '*', '@']:

                # swap them with ones in the inventory
                if currentState.boots[0][0] == color_matrix[L][C] and currentState.boots[0][1] < 3:
                    nextBoots = [(currentState.boots[0][0], currentState.boots[0][1] + 1)]
                    nextBoots.append((boots_matrix[l][c], 0))

                    nextState = State(stoneStatus, (L, C), nextBoots)

                    possibleStates.append((nextState, futureCost))

                # swap them with current ones
                if boots_matrix[l][c] == color_matrix[L][C]:
                    nextBoots = [(boots_matrix[l][c], 1)]
                    if len(currentState.boots) == 2 and currentState.boots[1][1] < 3:
                        nextBoots.append((currentState.boots[1][0], currentState.boots[1][1]))

                    nextState = State(stoneStatus, (L, C), nextBoots)

                    possibleStates.append((nextState, futureCost + 1))

    return possibleStates

def isFinalState(currentState):
    return currentState.gotStone and currentState.position == START_POSITION

def getHistory(currentState):
    global parent
    global dist

    stateHistory = []
    iteratorState = currentState
    while iteratorState != None:
        stateHistory.append(iteratorState)
        iteratorState = parent[iteratorState.id]

    stateHistory.reverse()
    return stateHistory

def writeHistoryToFile(filepath, history, time, cost):
    global solutionsFound

    if solutionsFound == 1:
        output_file = open(filepath, "wt")
    else:
        output_file = open(filepath, "a")

    output_file.write("###################################\n")
    output_file.write("Solution number " + str(solutionsFound) + ":\n")
    output_file.write("length: " + str(len(history)) + " cost: " + str(cost) + "\n")
    output_file.write("time: " + str(time) + "\n")
    output_file.write("nodes created: " + str(len(state_id_map)) + "\n")
    for state in history:
        output_file.write(str(state))

    output_file.close()

#### NOW GRAPH TRAVERSALS BEGIN

startingState = State(0, START_POSITION, [(color_matrix[START_POSITION[0]][START_POSITION[1]], 1)])

dist = defaultdict(defFactory)
parent = defaultdict(defFactory)
dist[1] = 0
parent[1] = None

solutionsFound = 0
TIMESTAMP_START = int(datetime.timestamp(datetime.now()))

# 1. depth-first search

done = False
def DFS(currentState):
    global solutionsFound
    global dist
    global parent
    global NSOL
    global done

    if solutionsFound == NSOL:
        return

    adjacentStates = getPossibleMoves(currentState)

    TIMESTAMP_NOW = datetime.timestamp(datetime.now())
    if TIMESTAMP_NOW - TIMESTAMP_START > TIMEOUT_SEC:
        done = True

    if isFinalState(currentState):
        solutionsFound += 1
        writeHistoryToFile(OUTPUT_FILEPATH + "/dfs_output.txt", getHistory(currentState), \
                round(datetime.timestamp(datetime.now()) - TIMESTAMP_START, 3), dist[currentState.id])

    for stateCost in adjacentStates:
        if (not stateCost[0].id in dist):
            dist[stateCost[0].id] = dist[currentState.id] + stateCost[1]
            parent[stateCost[0].id] = currentState
            DFS(stateCost[0])

#DFS(startingState)

# 2. Breadth-first search / Dijkstra
# because BFS can be seen as Dijkstra with a queue instead of a priority queue (heap)
# we can switch between BFS and Dijkstra just by redefining "pq"

# BFS
#pq = Queue()
# Dijkstra
pq = PriorityQueue()

done = False
pq.put((0, startingState))

while not done and pq.qsize() > 0:
    currentState = pq.get()[1]
    currentCost = dist[currentState.id]

    if isFinalState(currentState):
        solutionsFound += 1
        writeHistoryToFile(OUTPUT_FILEPATH + "/bfs_dijkstra_output.txt", getHistory(currentState), \
                round(datetime.timestamp(datetime.now()) - TIMESTAMP_START, 3), dist[currentState.id])
        if solutionsFound == NSOL:
            done = True
            break

    TIMESTAMP_NOW = datetime.timestamp(datetime.now())
    if TIMESTAMP_NOW - TIMESTAMP_START > TIMEOUT_SEC:
        done = True
        break

    adjacentStates = getPossibleMoves(currentState)

    for adjacentStateCost in adjacentStates:
        adj = adjacentStateCost[0].id
        cost = adjacentStateCost[1]

        # if adjacent state was not discovered yet
        # or we improved the cost to it (relaxed some edges)
        # we update the cost of it and put it into pq
        if (adj not in dist) or ((adj in dist) and dist[adj] > currentCost + cost):
            dist[adj] = currentCost + cost
            parent[adj] = currentState
            pq.put((currentCost + cost, adjacentStateCost[0]))

# 3. A* search (optimised)
# will be mostly same as Dijkstra but with a heuristic used
# to try to find most promising paths first

## 3.1 simple heuristic -> Manhattan distance to start
def heuristicDistance1(currentState):
    return abs(currentState.position[0] - START_POSITION[0]) + abs(currentState.position[1] - START_POSITION[1])

## 3.2 admissible heuristic 1 -> distance to start + 2 * Manhattan distance to stone IF stone is not taken

def heuristicDistance2(currentState):
    L = currentState.position[0]
    C = currentState.position[1]
    distance = heuristicDistance1(currentState)
    if not currentState.gotStone:
        distance += 2 * (abs(STONE_POSITION[0] - L) + abs(STONE_POSITION[1] - C))

    return distance

## 3.3 admissible heuristic 2 -> distance to start + distance to stone

def heuristicDistance3(currentState):
    return heuristicDistance1(currentState) - len(currentState.boots)

pq = PriorityQueue()
done = False
#pq.put((0, startingState))

while not done and pq.qsize() > 0:
    stateCost = pq.get()
    currentState = stateCost[1]
    currentCost = dist[currentState.id]

    if isFinalState(currentState):
        solutionsFound += 1
        writeHistoryToFile(OUTPUT_FILEPATH + "/a_star_output.txt", getHistory(currentState), \
                round(datetime.timestamp(datetime.now()) - TIMESTAMP_START, 3), dist[currentState.id])
        if solutionsFound == NSOL:
            done = True
            break

    TIMESTAMP_NOW = datetime.timestamp(datetime.now())
    if TIMESTAMP_NOW - TIMESTAMP_START > TIMEOUT_SEC:
        done = True
        break

    adjacentStates = getPossibleMoves(currentState)

    for adjacentStateCost in adjacentStates:
        adj = adjacentStateCost[0]
        cost = adjacentStateCost[1]

        # if adjacent state was not discovered yet
        # or we improved the cost to it (relaxed some edges)
        # we update the cost of it and put it into pq
        if (adj.id not in dist) or ((adj.id in dist) and dist[adj.id] > currentCost + cost):
            dist[adj.id] = currentCost + cost
            parent[adj.id] = currentState
            pq.put((currentCost + cost + heuristicDistance3(adj), adjacentStateCost[0]))

# 4. IDA*

done = False
threshold = heuristicDistance2(startingState)
minimum_over_threshold = 200000000000

def IDA(currentState):
    global solutionsFound
    global threshold
    global minimum_over_threshold
    global dist
    global parent
    global NSOL
    global done

    if solutionsFound == NSOL:
        return

    adjacentStates = getPossibleMoves(currentState)

    TIMESTAMP_NOW = datetime.timestamp(datetime.now())
    if TIMESTAMP_NOW - TIMESTAMP_START > TIMEOUT_SEC:
        done = True

    if isFinalState(currentState):
        solutionsFound += 1
        writeHistoryToFile(OUTPUT_FILEPATH + "/ida_star_output.txt", getHistory(currentState), \
                round(datetime.timestamp(datetime.now()) - TIMESTAMP_START, 3), dist[currentState.id])

    for stateCost in adjacentStates:
        if (not stateCost[0].id in dist):
            if dist[currentState.id] + stateCost[1] <= threshold:
                dist[stateCost[0].id] = dist[currentState.id] + stateCost[1]
                parent[stateCost[0].id] = currentState
                IDA(stateCost[0])
            else:
                minimum_over_threshold = min(minimum_over_threshold, dist[currentState.id] + stateCost[1])

#while not done:
    # resetting the search tree
    dist = defaultdict(defFactory)
    parent = defaultdict(defFactory)
    dist[1] = 0
    parent[1] = None
    minimum_over_threshold = 200000000000

    IDA(startingState)
    threshold = minimum_over_threshold

    TIMESTAMP_NOW = datetime.timestamp(datetime.now())
    if TIMESTAMP_NOW - TIMESTAMP_START > TIMEOUT_SEC:
        done = True

