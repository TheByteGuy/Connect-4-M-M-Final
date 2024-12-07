import asyncio
import websockets
import copy

# 0 for empty.... 1 for red.... 2 for yellow
# The board we use to keep track of all moves
brdState = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
]

"""
The scoring matrix using in our huerstics, here in real time we can
change the weight of hlw each piece is scored, higher number means
better score, a place on the board is better when it has a higher
amount of possible connect 4's you can get from it
"""
scoringMatrix = [
    [3, 4,  5,  7,  5, 4, 3],
    [4, 6,  8, 10,  8, 6, 4],
    [5, 8, 11, 13, 11, 8, 5],
    [5, 8, 11, 13, 11, 8, 5],
    [4, 6,  8, 10,  8, 6, 4],
    [3, 4,  5,  7,  5, 4, 3],
]


"""
Updates the broard aka brd state which is list of lists,
this is important as the moderator program does not do this
so we need to keep track of what the board looks like and make
sure we are not making any invalid moves as if we do we forfit
"""
def updateBrdState(col, player):
    for row in reversed(brdState):  # Start from the bottom row
        if row[col] == 0:  # Find the first empty slot
            row[col] = player
            break


"""
Check if there is a winning move on the board, by checking all possible
routes such as, diagnol left to right.. right to left and horizontal 
if there is it returns true, if there isnt it returns False
"""
def isWinningMove(brd, player):
    rows, cols = len(brd), len(brd[0])
    for r in range(rows):
        for c in range(cols):
            if c + 3 < cols:

                if all(brd[r][c + i] == player for i in range(4)):
                    return(True)
                
            if r + 3 < rows:
                if all(brd[r + i][c] == player for i in range(4)):
                    return(True)
                
            if r + 3 < rows and c + 3 < cols:
                if all(brd[r + i][c + i] == player for i in range(4)):
                    return(True)
                
            if r - 3 >= 0 and c + 3 < cols:
                if all(brd[r - i][c + i] == player for i in range(4)):
                    return(True)
                
    return(False)


"""
Heuristic evaluation of the brd using a scoring matrix, does pretty much same
thing as the score window function. And like stated above accounts for the scoring 
matrix which is essnetally the weight for good vers bad moves in the future, because
in the begining there are deffinitly better and worse moves, however the AI would see them
all in the same without this as it views moves off of what we told it to which is if they set 
us up in a good position for a win, so this is what keeps the ai in check in the begining 
making sure it makes good moves (which are the moves which have better chances of making a connect 4)
"""
def evalBrd(brd):
    score = 0
    for r in range(len(brd)):
        for c in range(len(brd[0])):
            if brd[r][c] == 1:  # AI's piece
                score += scoringMatrix[r][c]
            elif brd[r][c] == 2:  # Opponent's piece
                score -= scoringMatrix[r][c]

    # Evaluate windows for potential connections
    for row in brd:
        for c in range(4):
            window = row[c:c + 4]
            score += scoreWindow(window, 1)
            score -= scoreWindow(window, 2)
    return(score)


"""
Scores the window a couple of cells on the board, checks if we have a winning move if we do weighs
that extremly heavially as it means we will win, simarly checks for lower
amounts in a row and weights them, even changing score based on what our oppent
would get in that future, because if in three moves we win but in two they win we
would not like that future so this socres and accounts for that
"""
def scoreWindow(window, player, row=None, startCol=None):
    opponent = 2 if player == 1 else 1
    score = 0
    if window.count(player) == 4:
        score += 100

    elif window.count(player) == 3 and window.count(0) == 1:
        score += 5

    elif window.count(player) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent) == 3 and window.count(0) == 1:
        score -= 4

    if row is not None and startCol is not None:
        for i, cell in enumerate(window):
            if cell == player:
                score += scoringMatrix[row][startCol + i]

    return(score)



"""
Minimax algorithm with alpha-beta pruning, essentally
makes a bunch of different possible futures like a tree
with roots in the ground, then it searches through each possible
future, we use hueristics to determine if the root/future is good by
assiging values to the future, such as if there is a win for us the future
is good if there is a loss its bad
"""
def minimax(brd, depth, alpha, beta, maximizingPlayer):
    validMoves = [c for c in range(7) if brd[0][c] == 0]
    if isWinningMove(brd, 1):
        return None, 100000
    if isWinningMove(brd, 2):
        return None, -100000
    if depth == 0 or not validMoves:
        return None, evalBrd(brd)

    if maximizingPlayer:
        maxEval = -float('inf')
        bestCol = validMoves[0]
        for col in validMoves:
            tempBrd = copy.deepcopy(brd)
            updatebrdStateSim(tempBrd, col, 1)
            _, score = minimax(tempBrd, depth - 1, alpha, beta, False)
            if score > maxEval:
                maxEval = score
                bestCol = col
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return(bestCol, maxEval)
    else:
        minEval = float('inf')
        bestCol = validMoves[0]
        for col in validMoves:
            tempBrd = copy.deepcopy(brd)
            updatebrdStateSim(tempBrd, col, 2)
            _, score = minimax(tempBrd, depth - 1, alpha, beta, True)
            if score < minEval:
                minEval = score
                bestCol = col
            beta = min(beta, score)
            if alpha >= beta:
                break
        return(bestCol, minEval)


"""
Updates the brd state for simulation purposes, 
the params are brd (board), col (column), player which
is who is the player such as red or yellow, us or them
"""
def updatebrdStateSim(brd, col, player):
    for row in reversed(brd):
        if row[col] == 0:
            row[col] = player
            break


"""
Determines the next col to play based on the current brd state, and returns it. 
Does so by calling calc brd states, making sure its a valid move, 
then returns the move!
"""
def calcMove(oppMove):
    if oppMove is not None:
        updateBrdState(oppMove, 2)

    validMoves = [c for c in range(7) if brdState[0][c] == 0]
    if not validMoves:
        return(-1)

    bestCol, _ = minimax(brdState, 7, -float('inf'), float('inf'), True)
    updateBrdState(bestCol, 1)
    return(bestCol)



async def gameloop(socket, created):
    active = True
    while active:
        message = (await socket.recv()).split(':')
        match message[0]:
            case 'GAMESTART':
                print("Game started!")
                if created:
                    col = calcMove(None)
                    if col != -1:
                        await socket.send(f'PLAY:{col}')

            case 'ACK':
                print("Move acknowledged.")

            case 'OPPONENT':
                oppCol = int(message[1])
                print(f"Opponent played in column {oppCol}.")
                col = calcMove(oppCol)
                if col != -1:
                    await socket.send(f'PLAY:{col}')

            case 'WIN':
                print("You won! :))))))))))")
                active = False

            case 'LOSS':
                print("You lost :(((((((")
                active = False

            case 'DRAW':
                print("It's a draw! :3 ")
                active = False

            case 'TERMINATED':
                print("Game terminated?")
                active = False

            case 'ERROR':
                print(f"Error! :( : {message[1]}")
                active = False



async def create_game(server):
    async with websockets.connect(f'ws://{server}/create') as socket:
        await gameloop(socket, True)



async def join_game(server, id):
    async with websockets.connect(f'ws://{server}/join/{id}') as socket:
        await gameloop(socket, False)



if __name__ == '__main__':
    server = input('Server IP (WITHOUT HTTP://): ').strip()
    protocol = input('Join game or create game? (j/c): ').strip()
    match protocol:
        case 'c':
            asyncio.run(create_game(server))
        case 'j':
            id = input('Game ID: ').strip()
            asyncio.run(join_game(server, id))
        case _:
            print('Invalid protocol!')
