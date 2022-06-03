### Filipescu Radu - 251
### Micul Vrajitor

import numpy as np
from queue import PriorityQueue

### reading input data
from collections import defaultdict

INPUT_FILEPATH = "input.txt"
OUTPUT_FILEPATH = "output.txt"
NSOL = 1
TIMEOUT_TIME = 4000

## TO DO - input parameters from console

def defFactory():
    return 0
color_cost_map = defaultdict(defFactory)

input_file = open(INPUT_FILEPATH, "rt", encoding="utf-8")

input_line = input_file.readline()
while input_line != "----\n":
    input_line = input_line.split()
    color_cost_map[input_line[0]] = input_line[1]
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
    def __init__(self):
        self.gotStone = False
        self.position = (-1, -1)
        # boot type will be a list of tuples (boot-color, moves-done)
        # and always first ones will be the one currently equipped
        self.boots = []
        self.cost = 0

    def __init__(self, gotStone, position):
        self.gotStone = gotStone
        self.position = position
        self.boots = []
        self.cost = 0

def bootsAreOkay(boots, L, C):
    if boots_matrix[L][C] == color_matrix[L][C]:
        return True

    if len(boots) == 1:
        return boots[0][0] == color_matrix[L][C] and boots[0][1] < 3

    # else means that len(boots) == 2
    return (boots[0][0] == color_matrix[L][C] and boots[0][1] < 3) or \
           (boots[1][0] == color_matrix[L][C] and boots[1][1] < 3)

def getPossibleMoves(currentState):
    l = currentState.position[0]
    c = currentState.position[1]

    possibleStates = []
    adjacentPositions = [(l - 1, c), (l, c + 1), (l + 1, c), (l, c - 1)]

    for p in adjacentPositions:
        L = p[0]
        C = p[1]

        # if valid position and boots are ok
        if L > 0 and L < len(boots_matrix) and C > 0 and C < len(boots_matrix[0]) \
                and bootsAreOkay(currentState.boots, color_matrix[L][C]):

            ## these will be (kinda) common for all adjacent states
            stoneStatus = (boots_matrix[L][C] == '@' or currentState.gotStone)
            futureCost = currentState.cost + color_cost_map[color_matrix[L][C]]

            # step onto next state, using currently equipped boots
            if currentState.boots[0][0] == color_matrix[L][C] and currentState.boots[0][1] < 3:
                nextState = State(stoneStatus, futureCost)

                nextState.boots.append(currentState.boots[0])
                nextState.boots[0][1] += 1

                if len(currentState.boots) == 2:
                    nextState.boots.append(currentState.boots[1])
            # or step onto next state, swapping with boots in the inventory
            elif len(currentState) == 2 and currentState.boots[1][0] == color_matrix[L][C] \
                and currentState.boots[1][1] < 3:
                nextState.boots.append(currentState.boots[1])
                nextState.boots[0][1] += 1

                nextState.boots.append(currentState.boots[0])

                # swapping boots adds 1 cost
                nextState.cost += 1
            # or step onto next state, counting on the boots from there
            # and swapping them with the currently equipped ones
            elif color_matrix[L][C] == boots_matrix[L][C]:
                nextState.boots.append((boots_matrix[L][C], 0))
                if len(currentState.boots) == 2:
                    nextState.boots.append((currentState.boots[1]))
            # or step onto next state, counting on the boots from there
            # and swapping them with the ones in the inventory
            elif color_matrix[L][C] == boots_matrix[L][C] and len(currentState.boots) == 2:
                nextState


done = False
pq = PriorityQueue()

pq.put((0, State()))

while not done and pq.qsize() > 0:
    currentState = pq.get()

    edges = getPossibleMoves(currentState)