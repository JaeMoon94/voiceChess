import threading
import time

import pygame as p
from chess import ChessEngine, SmartMoveFinder
import speech_recognition as sr
import pyttsx3  # to create response
from transformers import pipeline
from queue import Queue
import re


class ChessMain:
    def __init__(self):
        self.WIDTH = self.HEIGHT = 512
        self.DIMENSION = 8
        self.SQ_SIZE = self.HEIGHT // self.DIMENSION
        self.MAX_FPS = 15
        self.IMAGES = {}

        self.q_movement = Queue()
        self.q_reverse = Queue()
        self.q_promotion = Queue()
        self.q_casting = Queue()
        self.q_position = Queue()
        self.q_reset = Queue()
        self.q_finish = Queue()
        self.q_stop = Queue()
        # q_endPosition = Queue()

        self.boardCombination = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'b1', 'b2',
                                 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'c1', 'c2', 'c3', 'c4',
                                 'c5', 'c6', 'c7', 'c8', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6',
                                 'd7', 'd8', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8',
                                 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'g1', 'g2',
                                 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'h1', 'h2', 'h3', 'h4',
                                 'h5', 'h6', 'h7', 'h8']

        self.positionQueue = []
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.candidate_labels = ['position change', 'reverse', 'cast', 'promotion', 'finish', 'restart', 'stop',
                                 'continue']
        self.promotion_candidate = ['pawn', 'rook', 'queen', 'knight', 'bishop']
        self.engine = pyttsx3.init()
        self.isStop = True
        self.isPawnPromotion = False

    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print('Calibrating...')
            r.adjust_for_ambient_noise(source)
            r.energy_threshold = 150
            print('Okay, go!')
            while self.isStop:

                '''
                Un Comment line 57 58 and 60 and comment out line 59  
                '''
                # audio = r.listen(source)
                # audio = r.record(source, duration=5)
                text = input("Enter your value: ")
                # text = r.recognize_google(audio)
                # print("You said " + text)
                self.engine.say(text)
                # engine.runAndWait()
                classified = self.classifier(text, self.candidate_labels, multi_label=True)
                print(classified['labels'][0])

                if "reverse" in classified['labels'][0]:
                    self.q_reverse.put(True)

                if "cast" in classified['labels'][0]:
                    self.q_casting.put(True)

                if "position change" == classified['labels'][0]:
                    userChoice = re.split("\s", text)

                    for el in userChoice:
                        if el in self.boardCombination:
                            self.positionQueue.append(el)

                    while len(self.positionQueue) != 0:
                        print(self.positionQueue)
                        self.q_position.put(self.positionQueue.pop(0))
                        # print(convertRowAndCol(q_startPosition.get()))

                    # else:
                    #     # We need to keep asking next question at this point
                    #     pass
                if "finish" == classified['labels'][0] or "continue" == classified['labels'][0]:
                    self.q_finish.put(False)

                if "restart" == classified['labels'][0]:
                    self.q_reset.put(True)

                if "stop" in classified['labels'][0]:
                    self.q_stop.put(True)

                if self.isPawnPromotion:
                    text = input("What do you want to promote? ")
                    # engine.say("What do you want to promote?")
                    promotion_classified = self.classifier(text, self.promotion_candidate, multi_label=True)
                    if "pawn" == promotion_classified['labels'][0]:
                        self.q_promotion.put('p')
                    elif "rook" == promotion_classified['labels'][0]:
                        self.q_promotion.put('R')
                    elif "queen" == promotion_classified['labels'][0]:
                        self.q_promotion.put('Q')
                    elif "knight" == promotion_classified['labels'][0]:
                        self.q_promotion.put('N')
                    elif "bishop" == promotion_classified['labels'][0]:
                        self.q_promotion.put('B')

    '''
    Initialize a global dictionaries of images. This will be called exactly once in the main
    '''

    def loadImages(self):
        pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            self.IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"),
                                                   (self.SQ_SIZE, self.SQ_SIZE))

    '''
    Main driver handle user input
    '''

    def main(self):
        p.init()
        screen = p.display.set_mode((self.WIDTH, self.HEIGHT))
        clock = p.time.Clock()
        screen.fill(p.Color("white"))
        gs = ChessEngine.GameState()

        listener = threading.Thread(target=self.listen)
        listener.start()

        validMoves = gs.getValidMoves()
        moveMade = False  # flag variable for when a move is made

        running = True
        sqSelected = ()  # no square is selected. Keep track of the last click of the user (tuple: (row,col))
        playerClicks = []  # keep track of player clicks( two tuples: [(6 , 4), (4, 4)])
        # Initialize Image
        self.loadImages()
        playerOne = True  # if a human is playing white, then this will be true.
        playerTwo = False  # if a human is playing black, then this will be true.
        while running:

            humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
            if self.q_finish.qsize() != 0:
                playerOne = self.q_finish.get(block=False, timeout=0.1)
            if self.q_stop.qsize() != 0:
                playerOne = self.q_stop.get(block=False, timeout=0.1)
            if p.event.get() == p.QUIT:
                self.isStop = False
                running = False

            # undoing and it has a bug
            elif self.q_reverse.qsize() != 0 and humanTurn:
                # elif classified['labels'][0] == 'reverse':
                if self.q_reverse.get(block=False,
                                      timeout=0.1):  # undo cmd+z for mac probably ctrl + z with windows machine
                    gs.undoMove()
                    moveMade = True
            while self.q_position.qsize() != 0:
                if humanTurn:
                    location = self.convertRowAndCol(self.q_position.get(block=False, timeout=0.1))
                    col = int(location[0])
                    row = int(location[1])
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
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            # print(move.getIsPawnToPromote())
                            if move.getIsPawnToPromote():
                                self.isPawnPromotion = True
                                time.sleep(3)
                                gs.whatToPromote(self.q_promotion.get(block=True))
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True

                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                                if move.isEnPassantMove:
                                    print("en passant")
                        if not moveMade:
                            playerClicks = [sqSelected]
            # AI move finder
            if not humanTurn:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True

            if moveMade:
                validMoves = gs.getValidMoves()
                moveMade = False

            if self.q_reset.qsize() != 0:
                if self.q_reset.get(block=False, timeout=0.1):
                    gs = ChessEngine.GameState()
                    playerOne = True
                    playerTwo = False
                    validMoves = gs.getValidMoves()
                    sqSelected = ()

            self.drawGameState(screen, gs, validMoves, sqSelected)
            clock.tick(self.MAX_FPS)
            p.display.flip()

    '''
    Highlight sqwuare selected and moves for piece selected
    '''

    def highlightSquare(self, screen, gs, validMoves, sqSelected):
        if sqSelected != ():
            r, c = sqSelected
            if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
                s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
                s.set_alpha(100)  # transparency Value -> transparent: 255 solid color
                s.fill(p.Color('blue'))
                screen.blit(s, (c * self.SQ_SIZE, r * self.SQ_SIZE))
                # highlight moves fom that square
                s.fill(p.Color('yellow'))
                for move in validMoves:
                    if move.startRow == r and move.startCol == c:
                        screen.blit(s, (self.SQ_SIZE * move.endCol, self.SQ_SIZE * move.endRow))

    '''
    Responsible for all the graphics within a current game state
    '''

    def drawGameState(self, screen, gs, validMoves, sqSelected):
        self.drawBoard(screen)  # draw Squares on the board
        self.highlightSquare(screen, gs, validMoves, sqSelected)
        self.drawPieces(screen, gs.board)  # draw pieces on top of those squares

    '''
    Draw the squares on the board.
    '''

    def drawBoard(self, screen):
        colors = [p.Color("white"), p.Color("gray")]
        font = p.font.SysFont('Raleway', 1, bold=True)
        green = (0, 0, 255)
        letter1 = font.render("8", False, green)
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                color = colors[(r + c) % 2]
                p.draw.rect(screen, color, p.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
                # screen.blit(letter1, (r, c))

    '''
    draw pieces on the board
    '''

    def drawPieces(self, screen, board):
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                piece = board[r][c]
                if piece != "--":  # not empty square
                    # print(IMAGES[piece])
                    screen.blit(self.IMAGES[piece],
                                p.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
                    # print(piece)

                    pass
        pass

    def convertRowAndCol(self, position):
        filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                       "5": 3, "6": 2, "7": 1, "8": 0}
        return filesToCols[position[0]], ranksToRows[position[1]]


if __name__ == "__main__":
    ChessMain().main()
