### Filipescu Radu - 251
### Micul Vrajitor
import itertools

import numpy as np
from queue import PriorityQueue, Queue

### reading input data
from collections import defaultdict

INPUT_FILEPATH = "input.txt"
OUTPUT_FILEPATH = "output.txt"
NSOL = 3
TIMEOUT_TIME = 4000

## TO DO - input parameters from console

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

def bootSetsAreEqual(boots1, boots2):
    if len(boots1) == 0 and len(boots2) == 0:
        return True

    if len(boots1) != len(boots2):
        return False

    if len(boots1) == 1:
        return boots1[0] == boots2[0]

    return (boots1[0] == boots2[0] and boots1[1] == boots2[1]) \
        or (boots1[0] == boots2[1] and boots1[1] == boots2[0])

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

#### NOW GRAPH TRAVERSALS BEGIN

startingState = State(0, START_POSITION, [(color_matrix[START_POSITION[0]][START_POSITION[1]], 1)])

dist = defaultdict(defFactory)
parent = defaultdict(defFactory)
dist[1] = 0
parent[1] = None

solutionsFound = 0

# 1. depth-first search
def DFS(currentState):
    global solutionsFound
    if solutionsFound == NSOL:
        return

    adjacentStates = getPossibleMoves(currentState)

    if isFinalState(currentState):
        print(getHistory(currentState))
        solutionsFound += 1

    for stateCost in adjacentStates:
        dist[stateCost[0]] = dist[currentState] + stateCost[1]
        parent[stateCost[0]] = currentState
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
#pq.put((0, startingState))

while not done and pq.qsize() > 0:
    stateCost = pq.get()
    currentCost = stateCost[0]
    currentState = dist[currentState.id]

    if isFinalState(currentState):
        print(getHistory(currentState))
        solutionsFound += 1
        if solutionsFound == NSOL:
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

# 3. A* search
# will be mostly same as Dijkstra but with a heuristic used
# to try to find most promising paths first

## 3.1 simple heuristic -> Manhattan distance to stone
def heuristicDistance1(currentState):
    return abs(currentState.position[0] - STONE_POSITION[0]) + abs(currentState.position[1] - STONE_POSITION[1])

## 3.2 admissible heuristic 1 -> distance to start + 2 * Manhattan distance to stone IF stone is not taken

def heuristicDistance2(currentState):
    distance = abs(currentState.position[0] - START_POSITION[0]) + abs(currentState.position[1] - START_POSITION[1])
    if not currentState.gotStone:
        distance += 2 * heuristicDistance1(currentState)

    return distance

## 3.3 admissible heuristic 2 -> distance to start + distance to stone

def heuristicDistance3(currentState):
    return heuristicDistance1(currentState) + \
           abs(currentState.position[0] - START_POSITION[0]) + abs(currentState.position[1] - START_POSITION[1])

pq = PriorityQueue()
done = False
pq.put((0, startingState))

while not done and pq.qsize() > 0:
    stateCost = pq.get()
    currentState = stateCost[1]
    currentCost = dist[currentState.id]

    if isFinalState(currentState):
        print(getHistory(currentState))
        solutionsFound += 1
        if solutionsFound == NSOL:
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