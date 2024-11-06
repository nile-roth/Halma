import tkinter as tk
from tkinter import *
import time
import math

CELL_SIZE = 40 #px
BOARD_SIZE = 10
SEARCH_TIME = 2 #seconds
row_labels = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
col_labels = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
pieces = {}
possMoveMarkers = {}
goalSquares = set()
pieceSelected = None
turn = 'W'

#for row in range(BOARD_SIZE):
    #for col in range(BOARD_SIZE):
        #if col < BOARD_SIZE-1:
            #print(gameBoard[row][col], end="  ")
        #else:
            #print(gameBoard[row][col])
            
def playHalma():
    global turn
    uiWindow = tk.Tk()

    window = tk.Canvas(uiWindow, width=(BOARD_SIZE+1)*CELL_SIZE, height=(BOARD_SIZE+1)*CELL_SIZE)
    window.pack()

    gameBoard = createBoard(window)
    gameBoard = setPieces(window, gameBoard)
    if turn != 'W':
        turn = 'W'

    def handleClick(event):
        global pieceSelected

        row = (event.y // CELL_SIZE) - 1
        col = (event.x // CELL_SIZE) - 1

        if row>=0 and row<BOARD_SIZE and col>=0 and col<BOARD_SIZE:
            #selecting a piece
            if gameBoard[row][col] == turn:
                if not pieceSelected or (pieceSelected and gameBoard[row][col] != 'E'):
                    clearMarkers(window)
                    setLegalMoves(gameBoard, (row,col), window, True)
                    pieceSelected = (row,col)

            #moving a piece
            elif pieceSelected and (row,col) in possMoveMarkers:
                movePiece(gameBoard, pieceSelected, (row,col), window)
                pieceSelected = None
                clearMarkers(window)
        
        winner = checkForEnd(gameBoard)
        if winner:
            displayWinner(uiWindow, window, winner)
    
    uiWindow.bind("<Button-1>", handleClick)

    #open window
    uiWindow.mainloop()


def createBoard(gui):
    #draw empty grid (USER INTERFACE)
    for row in range(BOARD_SIZE+1):
        for col in range(BOARD_SIZE+1):
            if row==0 and col==0:
                continue
            if row==0:
                gui.create_text(col*CELL_SIZE + CELL_SIZE/2, 20, text=row_labels[col-1], fill="black", font=('Helvetica 15'))
            elif col==0:
                gui.create_text(20, row*CELL_SIZE + CELL_SIZE/2, text=col_labels[row-1], fill="black", font=('Helvetica 15'))
            else:
                #draw rectangle
                x1 = col * CELL_SIZE 
                x2 = x1 + CELL_SIZE 
                y1 = row * CELL_SIZE 
                y2 = y1 + CELL_SIZE 

                gui.create_rectangle(x1, y1, x2, y2, outline="black")

    #FOR BACKEND
    board = [['E' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    return board

def setPieces(gui, board):
    global goalSquares

    #draw black pieces
    for row in range(1,int(BOARD_SIZE/2)+1):
        numPiecesInRow = int(BOARD_SIZE/2) - (row-1)
        for col in range(1,numPiecesInRow+1):
            #draw pieces
            x1 = col * CELL_SIZE 
            x2 = x1 + CELL_SIZE 
            y1 = row * CELL_SIZE 
            y2 = y1 + CELL_SIZE 

            board[row-1][col-1]='B'
            #create home square
            gui.create_rectangle(x1, y1, x2, y2, fill="grey")
            #create piece
            pieceID = gui.create_oval(x1+(BOARD_SIZE/4), y1+(BOARD_SIZE/4), x2-(BOARD_SIZE/4), y2-(BOARD_SIZE/4), fill="black")
            pieces[(row-1,col-1)] = pieceID
    
    #draw white pieces
    for row in range(BOARD_SIZE,int(BOARD_SIZE/2),-1):
        numPiecesInRow = int(BOARD_SIZE/2) - (BOARD_SIZE-row)
        for col in range(BOARD_SIZE,BOARD_SIZE-numPiecesInRow,-1):
            x1 = col * CELL_SIZE 
            x2 = x1 + CELL_SIZE 
            y1 = row * CELL_SIZE 
            y2 = y1 + CELL_SIZE 

            board[row-1][col-1]='W'

            #create home square
            gui.create_rectangle(x1, y1, x2, y2, fill="grey")
            #create piece
            pieceID = gui.create_oval(x1+(BOARD_SIZE/4), y1+(BOARD_SIZE/4), x2-(BOARD_SIZE/4), y2-(BOARD_SIZE/4), fill="white")
            pieces[(row-1,col-1)] = pieceID
            #add to agents goal
            goalSquares.add((row-1,col-1))

    return board

def setLegalMoves(gameBoard, pieceLocation, gui, visualize):
    global possMoveMarkers

    possMoves = [(pieceLocation[0]-1, pieceLocation[1]-1), (pieceLocation[0]-1, pieceLocation[1]), (pieceLocation[0]-1, pieceLocation[1]+1),
                 (pieceLocation[0], pieceLocation[1]-1),                                           (pieceLocation[0], pieceLocation[1]+1),
                 (pieceLocation[0]+1, pieceLocation[1]-1), (pieceLocation[0]+1, pieceLocation[1]), (pieceLocation[0]+1, pieceLocation[1]+1)]
        
    def getJumps(location, jumped, visited):
        visited.add(location)

        newPossMoves = [(location[0]-1, location[1]-1), (location[0]-1, location[1]), (location[0]-1, location[1]+1),
                        (location[0], location[1]-1),                                 (location[0], location[1]+1),
                        (location[0]+1, location[1]-1), (location[0]+1, location[1]), (location[0]+1, location[1]+1)]
        newPossMoves.remove(jumped)

        for move in newPossMoves:

            if isInBounds(move) and not isEmpty(move, gameBoard):
                posDifference = (move[0] - location[0], move[1] - location[1])
                jumpCoord = (move[0] + posDifference[0], move[1] + posDifference[1])

                if isInBounds(jumpCoord) and isEmpty(jumpCoord, gameBoard) and jumpCoord not in visited:
                    if jumpCoord not in legalMoves:
                        legalMoves.append(jumpCoord)
                    getJumps(jumpCoord, move, visited)

        return
    
    def vizLegalMoves(movesList):
        global possMoveMarkers

        x1 = (pieceLocation[1]+1) * CELL_SIZE 
        x2 = x1 + CELL_SIZE 
        y1 = (pieceLocation[0]+1) * CELL_SIZE 
        y2 = y1 + CELL_SIZE 
        row = (((y1+y2)/2) // CELL_SIZE) - 1
        col = (((x1+x2)/2) // CELL_SIZE) - 1

        markerID = gui.create_rectangle(x1, y1, x2, y2, outline="red")
        possMoveMarkers[(row,col)] = markerID  

        for move in movesList:
            x1 = (move[1] + 1) * CELL_SIZE + CELL_SIZE / 2
            y1 = (move[0] + 1) * CELL_SIZE + CELL_SIZE / 2
            markerID = gui.create_text(x1, y1, text="+", fill="red", font=('Helvetica 15'))
            possMoveMarkers[(move[0],move[1])] = markerID

    if isEmpty(pieceLocation, gameBoard):
        return 
    
    legalMoves = []

    for move in possMoves:
        if isInBounds(move) and isEmpty(move, gameBoard):
            legalMoves.append(move)
        elif isInBounds(move) and not isEmpty(move, gameBoard):
            posDifference = (move[0] - pieceLocation[0], move[1] - pieceLocation[1])
            jumpCoord = (move[0] + posDifference[0], move[1] + posDifference[1])
            if isInBounds(jumpCoord) and isEmpty(jumpCoord, gameBoard):
                if jumpCoord not in legalMoves:
                    legalMoves.append(jumpCoord)
                getJumps(jumpCoord, move, set())

    if visualize:
        vizLegalMoves(legalMoves)
    return legalMoves

def isInBounds(location):
    if location[0] >= 0 and location[0] < BOARD_SIZE:
        if location[1] >= 0 and location[1] < BOARD_SIZE:
            return True
    return False

def isEmpty(location, gameBoard):
    if gameBoard[location[0]][location[1]] == 'E':
        return True

def clearMarkers(gui):
    global possMoveMarkers
    for markerID in possMoveMarkers.values():
        gui.delete(markerID)
    possMoveMarkers = {}

def movePiece(gameBoard, pieceLocation, moveToLocation, gui):
    global turn
    if turn == 'W':
        turn = 'B'
    else:
        turn = 'W'
    gui.delete(pieces.get(pieceLocation))
    del pieces[pieceLocation]

    #get color of piece
    pieceColor = gameBoard[pieceLocation[0]][pieceLocation[1]]
    gameBoard[pieceLocation[0]][pieceLocation[1]] = 'E'

    gameBoard[moveToLocation[0]][moveToLocation[1]] = pieceColor

    x1 = (moveToLocation[1]+1) * CELL_SIZE 
    x2 = x1 + CELL_SIZE 
    y1 = (moveToLocation[0]+1) * CELL_SIZE 
    y2 = y1 + CELL_SIZE 
    if pieceColor=='W':
        pieceID = gui.create_oval(x1+(BOARD_SIZE/4), y1+(BOARD_SIZE/4), x2-(BOARD_SIZE/4), y2-(BOARD_SIZE/4), fill="white")
    else:
        pieceID = gui.create_oval(x1+(BOARD_SIZE/4), y1+(BOARD_SIZE/4), x2-(BOARD_SIZE/4), y2-(BOARD_SIZE/4), fill="black")
    
    pieces[moveToLocation] = pieceID

def checkForEnd(gameBoard):
    whiteWon = True
    blackWon = True

    goalSquaresBlack = goalSquares
    goalSquaresWhite = set()
    for row in range(1,int(BOARD_SIZE/2)+1):
        numPiecesInRow = int(BOARD_SIZE/2) - (row-1)
        for col in range(1,numPiecesInRow+1):
            goalSquaresWhite.add((row-1,col-1))

    for square in goalSquaresWhite:
        if gameBoard[square[0]][square[1]] != 'W':
            whiteWon = False
    
    for square in goalSquaresBlack:
        if gameBoard[square[0]][square[1]] != 'B':
            blackWon = False

    if whiteWon:
        return 'W'
    elif blackWon:
        return 'B'
    
    return False

def displayWinner(uiWindow, window, won):
    global turn
    winner = 'White' if won == 'W' else 'Black'
    
    # Destroy the game board to clear it from the screen
    window.destroy()

    # Prevent further clicks on the board by unbinding the event
    uiWindow.unbind("<Button-1>")

    # Create and set up the game over alert window
    alertDim = int(((BOARD_SIZE+1) * CELL_SIZE) / 2)  # Half the size of original window
    gameOverAlert = Toplevel(uiWindow)
    gameOverAlert.geometry(f"{alertDim}x{alertDim}")
    gameOverAlert.title("Game Over")

    # Display the winner message
    Label(gameOverAlert, text=f"{winner} wins!", font=('Helvetica 20 bold')).pack(pady=20)

    # Function to restart the game
    def playAgain():
        gameOverAlert.destroy()
        uiWindow.destroy()  # Close the main window completely
        playHalma()         # Restart the game

    # Button to play again
    Button(gameOverAlert, text="Play Again", font=('Helvetica 15'), command=playAgain).pack(pady=10)

#RUNS FOR BLACK ONLY
def minimax(board, depth):
    def simulateMove(boardCopy, location, moveTo):
        boardCopy[location[0]][location[1]] = 'E'
        boardCopy[moveTo[0]][moveTo[1]] = 'B'

    if depth == 0 or checkForEnd(board):
        return evaluateBoard(board), None

    best_move = None
    min_eval = float('inf')
    for piece, moves in generateMoves(board, 'B').items():
        for move in moves:
            board_copy = [row[:] for row in board]
            simulateMove(board_copy, piece, move)
            eval_score = minimax(board_copy, depth - 1)[0]
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (piece, move)

    return min_eval, best_move

def generateMoves(board, color):
    moves = {}
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == color:
                possible_moves = setLegalMoves(board, (row, col), None, visualize=False)
                if possible_moves:
                    moves[(row, col)] = possible_moves
    return moves

def evaluateBoard(board):
    black_distance = sum(manhattanDist(piece, goal) for piece, goal in goalSquares if board[piece[0]][piece[1]] == 'B')
    white_distance = sum(manhattanDist(piece, goal) for piece, goal in goalSquares if board[piece[0]][piece[1]] == 'W')
    return white_distance - black_distance


def manhattanDist(piece, goal):
    return abs(piece[0] - goal[0]) + abs(piece[1] - goal[1])      

playHalma()
