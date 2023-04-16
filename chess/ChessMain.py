import threading

import pygame as p
from chess import ChessEngine, SmartMoveFinder
import speech_recognition as sr
import pyttsx3  # to create response
from transformers import pipeline
from queue import Queue
import re

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

q_movement = Queue()
q_reverse = Queue()
q_promotion = Queue()
q_casting = Queue()
q_startPosition = Queue()
q_endPosition = Queue()

boardCombination = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'b1', 'b2',
                    'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'c1', 'c2', 'c3', 'c4',
                    'c5', 'c6', 'c7', 'c8', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6',
                    'd7', 'd8', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8',
                    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'g1', 'g2',
                    'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'h1', 'h2', 'h3', 'h4',
                    'h5', 'h6', 'h7', 'h8']

positionQueue = []

classifier = pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ['position change', 'reverse', 'cast', 'promotion']
promotion_candidate = ['pawn', 'rook', 'queen', 'knight', 'bishop']
engine = pyttsx3.init()
isStop = True


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Calibrating...')
        r.adjust_for_ambient_noise(source)
        r.energy_threshold = 150
        print('Okay, go!')
        while isStop:
            # audio = r.listen(source)
            # audio = r.record(source, duration=5)
            text = input("Enter your value: ")
            # text = r.recognize_google(audio)
            print("You said " + text)
            engine.say(text)
            # engine.runAndWait()
            classified = classifier(text, candidate_labels, multi_label=True)
            print(classified)

            if "reverse" in classified['labels'][0]:
                q_reverse.put(True)

            if "promotion" in classified['labels'][0]:
                # text = r.listen(source)
                text = input("What do you want to promote? ")
                classified = classifier(text, promotion_candidate, multi_lable=True)
                print("You choose : " + classified['labels'][0])
                q_promotion.put(classified['labels'][0])

            if "cast" in classified['labels'][0]:
                q_casting.put(True)
            if "position change" in classified['labels'][0]:
                userChoice = re.split("\s", text)
                for el in userChoice:
                    if el in boardCombination:
                        positionQueue.append(el)

                        if positionQueue == 2:
                            print(positionQueue)
                            q_startPosition = positionQueue.pop(0)
                            print(positionQueue)
                            q_endPosition = positionQueue.pop(0)
                            print(positionQueue)
                        else:
                            # We need to keep asking next question at this point
                            pass


'''
Initialize a global dictionaries of images. This will be called exactly once in the main
'''


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


'''
Main driver handle user input
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()

    # listener = threading.Thread(target=listen)
    # listener.start()

    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made

    running = True
    sqSelected = ()  # no square is selected. Keep track of the last click of the user (tuple: (row,col))
    playerClicks = []  # keep track of player clicks( two tuples: [(6 , 4), (4, 4)])
    # Initialize Image
    loadImages()
    playerOne = True  # if a human is playing white, then this will be true.
    playerTwo = False  # if a human is playing black, then this will be true.
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                isStop = False
                running = False
            # Mouse Handelr
            elif e.type == p.MOUSEBUTTONDOWN:
                if humanTurn:
                    location = p.mouse.get_pos()  # (x, y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # the user clicked the same square twice
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:

                        '''
                            put parsed user voice input to here
                        '''
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both first and second clicks

                    # was that the user second click
                    if len(playerClicks) == 2:  # after the second click

                        # Player Clicks[0] indicates initial move from the user
                        # Player Clicks[1] indicates final move from the user.
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        # print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                                if move.isEnPassantMove:
                                    print("en passant")
                        if not moveMade:
                            playerClicks = [sqSelected]

                # key handlers
            if q_reverse.qsize() != 0:
                # elif classified['labels'][0] == 'reverse':
                if q_reverse.get(block=False,
                                 timeout=0.1):  # undo cmd+z for mac probably ctrl + z with windows machine
                    gs.undoMove()
                    moveMade = True

        # AI move finder
        if not humanTurn:
            AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True


        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Highlight sqwuare selected and moves for piece selected
'''


def highlightSquare(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency Value -> transparent: 255 solid color
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves fom that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))


'''
Responsible for all the graphics within a current game state
'''


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # draw Squares on the board
    highlightSquare(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


'''
Draw the squares on the board.
'''


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    font = p.font.SysFont('Raleway', 1, bold=True)
    green = (0, 0, 255)
    letter1 = font.render("8", False, green)
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            # screen.blit(letter1, (r, c))


'''
draw pieces on the board
'''


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                # print(IMAGES[piece])
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                # print(piece)

                pass
    pass


if __name__ == "__main__":
    main()
