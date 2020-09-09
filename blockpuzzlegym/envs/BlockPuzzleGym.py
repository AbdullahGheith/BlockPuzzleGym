import gym
import random
from array import array
import pyglet
from gym import spaces
import numpy as np
from time import sleep
from tkinter import *
from gym.envs.classic_control import rendering
import math

puzzlepiece1 = np.array([[1]])

puzzlepiece2 = np.array([[1, 1, 1, 1, 1]])

puzzlepiece3 = np.array([[1, 1, 1, 1]])

puzzlepiece4 = np.array([[1, 1],
                         [1]])

puzzlepiece5 = np.array([[1, 1],
                         [1, 1]])

puzzlepiece6 = np.array([[1, 1, 1]])

puzzlepiece7 = np.array([[1, 1, 1],
                         [1, 1, 1],
                         [1, 1, 1]])

puzzlepiece8 = np.array([[1, 1],
                         [1, 1]])

puzzlepiece9 = np.array([[1],
                         [1, 1, 1]])

puzzlepiece10 = np.array([[1],
                          [1],
                          [1],
                          [1]])

puzzlepiece11 = np.array([[1, 1, 1],
                          [0, 0, 1],
                          [0, 0, 1]])

puzzlepieces = [puzzlepiece1, puzzlepiece2, puzzlepiece3, puzzlepiece4, puzzlepiece5, puzzlepiece6, puzzlepiece7,
                puzzlepiece8, puzzlepiece9, puzzlepiece10, puzzlepiece11]


class BlockPuzzleGym(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(BlockPuzzleGym, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        height = 8
        width = 8

        self.currentPuzzleNo1 = None
        self.currentPuzzle1 = None
        self.currentPuzzleNo2 = None
        self.currentPuzzle2 = None
        self.currentPuzzleNo3 = None
        self.currentPuzzle3 = None
        self.transform = None
        self.poletrans = None
        self.window = None
        self.board = np.full((height, width), False)
        self.viewer = None
        self.totalBlocksPlaced = 0
        self.height = height
        self.width = width
        self.reward = 0
        self.renderCells = None
        self.renderPuzzlePiece1 = None
        self.renderPuzzlePiece2 = None
        self.renderPuzzlePiece3 = None
        self.newPuzzlePieces()

        self.action_space = spaces.MultiDiscrete([3, width * height])
        # Example for using image as input:
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(self.width + 1, self.height), dtype=np.float32)
        # print(self.observation_space)
        # self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        # Example for using image as input:
        # self.observation_space = spaces.Box(low=0, high=255, shape=(HEIGHT, WIDTH, N_CHANNELS), dtype=np.uint8)

        self.renderWidth = 320
        self.renderHeight = 240
        self.boardCellHeightAndWidth = 20

    def step(self, action):
        chosenPuzzleArrayNo = action[0]
        chosenMove = action[1]
        assert chosenMove < self.width * self.height + 1

        chosenPuzzle = None
        if chosenPuzzleArrayNo == 0:
            chosenPuzzle = self.currentPuzzle1
        elif chosenPuzzleArrayNo == 1:
            chosenPuzzle = self.currentPuzzle2
        elif chosenPuzzleArrayNo == 2:
            chosenPuzzle = self.currentPuzzle3

        if chosenPuzzle is None:
            self.reward -= 0.001
        else:
            if self.insertPiece(chosenPuzzle, chosenMove):

                if chosenPuzzleArrayNo == 0:
                    self.currentPuzzle1 = None
                    self.currentPuzzleNo1 = None
                elif chosenPuzzleArrayNo == 1:
                    self.currentPuzzle2 = None
                    self.currentPuzzleNo2 = None
                elif chosenPuzzleArrayNo == 2:
                    self.currentPuzzle3 = None
                    self.currentPuzzleNo3 = None

                self.checkWin()
                self.newPuzzlePieces()
            else:
                self.reward -= 0.001

        #print("Reward: " + str(self.reward))
        # print("Total Blocks Placed: " + str(self.totalBlocksPlaced))

        return self.sumBoard(), self.reward, self.checkIfDead(), {}

    def reset(self):
        self.reward = 0
        self.newPuzzlePieces()
        self.totalBlocksPlaced = 0
        self.board = np.full((self.height, self.width), False)
        return self.sumBoard()

    def sumBoard(self):
        # boardInOne = np.array(([1,1],[0,0]))
        boardInOne = np.append(self.board.astype('float32'), [
            [self.sumPuzzlePiece(self.currentPuzzleNo1), self.sumPuzzlePiece(self.currentPuzzleNo2),
             self.sumPuzzlePiece(self.currentPuzzleNo3), 0, 0, 0, 0, 0]], axis=0)
        # for idx, valx in enumerate(self.board):
        #    for idy, valy in enumerate(valx):
        #        boardInOne = np.append(boardInOne, int(valy))

        # boardInOne = np.append(boardInOne, self.currentPuzzle)
        return boardInOne

    def sumPuzzlePiece(self, puzzleNo):
        if puzzleNo is None:
            return 0
        else:
            return puzzleNo / len(puzzlepieces)

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None

    def render(self, mode='human', close=False):

        screenheight = 800
        screenwidth = 900
        cellSize = 40
        cellpadding = 5
        l, r, t, b = -cellSize / 2, cellSize / 2, cellSize / 2, -cellSize / 2
        currentx = 0
        currenty = 0
        if self.viewer is None:
            self.viewer = rendering.Viewer(screenwidth, screenheight)
            self.renderCells = np.array([])
            for vertical in self.board:
                for cell in vertical:
                    poly = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
                    poly_transform = rendering.Transform()
                    poly_transform.set_translation(currentx + 330, screenheight - currenty - 50)
                    poly.add_attr(poly_transform)
                    if (cell == 0):
                        poly.set_color(252 / 256, 186 / 256, 3 / 256)  # yellow
                    else:
                        poly.set_color(50 / 256, 171 / 256, 64 / 256)  # green
                    self.viewer.add_geom(poly)
                    self.renderCells = np.append(self.renderCells, poly)
                    currentx += cellSize + cellpadding
                currenty += cellSize + cellpadding
                currentx = 0

            self.renderPuzzlePieceFunction1(0, screenheight, cellSize, cellpadding, l, r, t, b)
            self.renderPuzzlePieceFunction2(300, screenheight, cellSize, cellpadding, l, r, t, b)
            self.renderPuzzlePieceFunction3(600, screenheight, cellSize, cellpadding, l, r, t, b)

        self.renderPuzzlePieceFunction1(0, screenheight, cellSize, cellpadding, l, r, t, b)
        self.renderPuzzlePieceFunction2(300, screenheight, cellSize, cellpadding, l, r, t, b)
        self.renderPuzzlePieceFunction3(600, screenheight, cellSize, cellpadding, l, r, t, b)

        for idx, valx in enumerate(self.renderCells):
            val = self.getValueForplaceOnBoard(idx)
            if (val == 0):
                valx.set_color(252 / 256, 186 / 256, 3 / 256)  # yellow
            else:
                valx.set_color(50 / 256, 171 / 256, 64 / 256)  # green
        #print("Current reward: " + str(self.reward))
        return self.viewer.render(return_rgb_array=mode == 'rgb_array')
        # w.create_line(150, 80, 200, 100, fill="#476042", width=3)

        # if mode == 'human':
        # img = Image.new('RGB', (self.renderHeight, self.renderWidth), color=(255,255,255))
        # d = ImageDraw.Draw(img)
        # d.text((10, 10), "Hello World", fill=(255, 255, 0))
        # if self.viewer is None:
        #     self.viewer = rendering.SimpleImageViewer()
        # self.viewer.imshow(img)
        # return self.viewer.isopen
        # else:
        # print()
        # print()
        # print()
        # print()
        # print()
        # print("Reward: " + str(self.reward))
        # print("Total Blocks Placed: " + str(self.totalBlocksPlaced))
        # for x in range(self.height):
        #     print()
        #     for y in range(self.width):
        #         print(int(self.board[x][y]), end=",")

    def renderPuzzlePieceFunction1(self, xPadding, screenheight, cellSize, cellpadding, l, r, t, b):
        currentx = 0
        currenty = 0
        if self.currentPuzzle1 is not None:
            self.renderPuzzlePiece1 = np.array([])
            for vertical in self.currentPuzzle1:
                for cell in vertical:
                    poly = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
                    poly_transform = rendering.Transform()
                    poly_transform.set_translation(currentx + 50 + xPadding, screenheight - currenty - 450)
                    poly.add_attr(poly_transform)
                    if (cell == 1):
                        poly.set_color(235 / 256, 64 / 256, 52 / 256)  # red
                    else:
                        poly.set_color(1, 1, 1) #white
                    self.viewer.add_geom(poly)
                    self.renderPuzzlePiece1 = np.append(self.renderPuzzlePiece1, poly)
                    currentx += cellSize + cellpadding
                currenty += cellSize + cellpadding
                currentx = 0
        else:
            if self.renderPuzzlePiece1 is not None:
                for poly in self.renderPuzzlePiece1:
                    poly.set_color(1,1,1)

    def renderPuzzlePieceFunction2(self, xPadding, screenheight, cellSize, cellpadding, l, r, t, b):
        currentx = 0
        currenty = 0
        if self.currentPuzzle2 is not None:
            self.renderPuzzlePiece2 = np.array([])
            for vertical in self.currentPuzzle2:
                for cell in vertical:
                    poly = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
                    poly_transform = rendering.Transform()
                    poly_transform.set_translation(currentx + 50 + xPadding, screenheight - currenty - 450)
                    poly.add_attr(poly_transform)
                    if (cell == 1):
                        poly.set_color(235 / 256, 64 / 256, 52 / 256)  # red
                    else:
                        poly.set_color(1, 1, 1) #white
                    self.viewer.add_geom(poly)
                    self.renderPuzzlePiece2 = np.append(self.renderPuzzlePiece2, poly)
                    currentx += cellSize + cellpadding
                currenty += cellSize + cellpadding
                currentx = 0
        else:
            if self.renderPuzzlePiece2 is not None:
                for poly in self.renderPuzzlePiece2:
                    poly.set_color(1,1,1)

    def renderPuzzlePieceFunction3(self, xPadding, screenheight, cellSize, cellpadding, l, r, t, b):
        currentx = 0
        currenty = 0
        if self.currentPuzzle3 is not None:
            self.renderPuzzlePiece3 = np.array([])
            for vertical in self.currentPuzzle3:
                for cell in vertical:
                    poly = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
                    poly_transform = rendering.Transform()
                    poly_transform.set_translation(currentx + 50 + xPadding, screenheight - currenty - 450)
                    poly.add_attr(poly_transform)
                    if (cell == 1):
                        poly.set_color(235 / 256, 64 / 256, 52 / 256)  # red
                    else:
                        poly.set_color(1, 1, 1) #white
                    self.viewer.add_geom(poly)
                    self.renderPuzzlePiece3 = np.append(self.renderPuzzlePiece3, poly)
                    currentx += cellSize + cellpadding
                currenty += cellSize + cellpadding
                currentx = 0
        else:
            if self.renderPuzzlePiece3 is not None:
                for poly in self.renderPuzzlePiece3:
                    poly.set_color(1,1,1)

    def newPuzzlePieces(self):
        if self.currentPuzzle1 is None and self.currentPuzzle2 is None and self.currentPuzzle3 is None:
            self.currentPuzzleNo1 = random.randint(0, len(puzzlepieces) - 1)
            self.currentPuzzle1 = puzzlepieces[self.currentPuzzleNo1]
            self.currentPuzzleNo2 = random.randint(0, len(puzzlepieces) - 1)
            self.currentPuzzle2 = puzzlepieces[self.currentPuzzleNo2]
            self.currentPuzzleNo3 = random.randint(0, len(puzzlepieces) - 1)
            self.currentPuzzle3 = puzzlepieces[self.currentPuzzleNo3]

            # self.currentPuzzleNo1 = 10
            # self.currentPuzzle1 = puzzlepieces[10]
            # self.currentPuzzleNo2 = 10
            # self.currentPuzzle2 = puzzlepieces[10]
            # self.currentPuzzleNo3 = 10
            # self.currentPuzzle3 = puzzlepieces[10]

            if self.renderPuzzlePiece1 is not None:
                for poly in self.renderPuzzlePiece1:
                    poly.set_color(1,1,1)
            if self.renderPuzzlePiece2 is not None:
                for poly in self.renderPuzzlePiece2:
                    poly.set_color(1,1,1)
            if self.renderPuzzlePiece3 is not None:
                for poly in self.renderPuzzlePiece3:
                    poly.set_color(1,1,1)

    def insertPiece(self, puzzle, place):
        if self.pieceFits(puzzle, place):
            for idx, valx in enumerate(puzzle):
                currentBoardY, currentBoardX = self.placeToPlaceOnBoard(place)
                for idy, valy in enumerate(valx):
                    if valy == 1:
                        self.board[currentBoardY][currentBoardX] = 1
                    currentBoardX += 1
                place += self.width
            self.reward += self.countBlocksInPiece(puzzle)
            self.totalBlocksPlaced += 1
            return True
        return False

    def countBlocksInPiece(self, puzzle):
        count = 0
        for idx, valx in enumerate(puzzle):
            for idy, valy in enumerate(valx):
                count += 1
        return count

    def pieceFits(self, puzzle, place):
        try:
            for idx, valx in enumerate(puzzle):
                currentBoardY, currentBoardX = self.placeToPlaceOnBoard(place)
                for idy, valy in enumerate(valx):
                    if valy == 1:
                        if self.board[currentBoardY][currentBoardX] == 1:
                            return False
                    currentBoardX += 1
                place += self.width
        except Exception as e:
            return False
        return True

    def placeToPlaceOnBoard(self, place):
        if place < self.width:
            currentBoardY = 0
            currentBoardX = place
        else:
            currentBoardX = place % self.width
            currentBoardY = math.floor(place/self.width)

        return currentBoardY, currentBoardX


    def getValueForplaceOnBoard(self, place):
        if place < self.width:
            currentBoardY = 0
            currentBoardX = place
        else:
            currentBoardX = place % self.width
            currentBoardY = math.floor(place/self.width)

        return self.board[currentBoardY][currentBoardX]


    def checkWinLineHorizontal(self):

        winningHorizontals = np.array([])
        for i in range(self.width):
            allones = True
            for idx, val in enumerate(self.board):
                if val[i] == 0:
                    allones = False
                    break
            if allones:
                winningHorizontals = np.append(winningHorizontals, i)

        return winningHorizontals

    def getPoints(self, lines):
        previous = 0
        for x in range(lines + 1):
            previous = x * 10 + previous
        return previous

    def checkWin(self):
        verticals = self.checkWinLineVertical()
        horizontals = self.checkWinLineHorizontal()
        linesCleared = len(verticals) + len(horizontals)
        if linesCleared > 0:
            self.reward += self.getPoints(linesCleared)
            self.clearHorizontalLine(horizontals)
            self.clearVerticalLine(verticals)

    def checkIfDead(self):
        first = True
        second = True
        third = True
        if self.currentPuzzle1 is not None:
            first = self.checkIfDeadForPiece(self.currentPuzzle1)
        if self.currentPuzzle2 is not None:
            second = self.checkIfDeadForPiece(self.currentPuzzle2)
        if self.currentPuzzle3 is not None:
            third = self.checkIfDeadForPiece(self.currentPuzzle3)
        return first and second and third

    def checkIfDeadForPiece(self, puzzle):
        for x in range(self.width * self.height):
            if self.pieceFits(puzzle, x):
                return False
        return True

    def checkWinLineVertical(self):

        winningVerticals = np.array([])
        for idx, valx in enumerate(self.board):
            allones = True
            for idy, valy in enumerate(valx):
                if valy == 0:
                    allones = False
                    break
            if allones:
                winningVerticals = np.append(winningVerticals, idx)

        return winningVerticals

    def clearHorizontalLine(self, columns):
        for cols in columns:
            for y in range(len(self.board)):
                self.board[y][int(cols)] = 0

    def clearVerticalLine(self, rows):
        for row in rows:
            for x in range(len(self.board[int(row)])):
                self.board[int(row)][x] = 0
