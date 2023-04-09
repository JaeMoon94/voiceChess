import pygame as p
from chess import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


# import speech_recognition as sr
# import pyttsx3 # to create response
# import spacy# package to extract the features
# from transformers import pipeline
#
# r = sr.Recognizer()
# nlp = spacy.load("en_core_web_md")
# # classifier = pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')
# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
# candidate_labels = ['place', 'reverse', 'asking advice']



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

    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made

    running = True
    sqSelected = ()  # no square is selected. Keep track of the last click of the user (tuple: (row,col))
    playerClicks = []  # keep track of player clicks( two tuples: [(6 , 4), (4, 4)])
    # Initialize Image
    loadImages()
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse Handelr
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col):  # the user clicked the same square twice
                    sqSelected = ()  # deselect
                    playerClicks = []  # clear player clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)  # append for both first and second clicks

                # was that the user second click
                if len(playerClicks) == 2:  # after the second click

                    # Player Clicks[0] indicates initial move from the user
                    # Player Clicks[1] indicates final move from the user.
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        sqSelected = ()  # reset user clicks
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]

            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo cmd+z for mac probably ctrl + z with windows machine
                    gs.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Responsible for all the graphics within a current game state
'''


def drawGameState(screen, gs):
    drawBoard(screen)  # draw Squares on the board
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


'''
Draw the squares on the board.
'''


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


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
