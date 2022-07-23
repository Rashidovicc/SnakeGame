import sys
import random
import math
from win32api import GetSystemMetrics
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = QVBoxLayout()

        self.pointsTextLabel = QLabel("Points:")

        self.pointsLabel = QLabel("0/5")
        self.pointsLabel.setStyleSheet("border: none")

        self.levelTextLabel = QLabel("Level:")

        self.levelLabel = QLabel("1")
        self.levelLabel.setStyleSheet("border: none"),

        self.timeTextLabel = QLabel("Elapsed Time:")

        self.timeLabel = QLabel("00:00")
        self.timeLabel.setStyleSheet("border: none")

        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet("background: #333; color: #fff; font-size: 16px; border: none")
        self.statusbar.setMaximumHeight(20)
        self.statusbar.addWidget(self.pointsTextLabel)
        self.statusbar.addWidget(self.pointsLabel)
        self.statusbar.addWidget(self.levelTextLabel)
        self.statusbar.addWidget(self.levelLabel)
        self.statusbar.addWidget(self.timeTextLabel)
        self.statusbar.addWidget(self.timeLabel)

        
        self.gameOverBox = QMessageBox()
        self.gameOverBox.setWindowTitle("GAME OVER")
        self.gameOverBoxButton1 = self.gameOverBox.addButton("Retry", self.gameOverBox.ActionRole)
        self.gameOverBoxButton1.clicked.connect(self.restart_game)
        self.gameOverBoxButton2 = self.gameOverBox.addButton("Exit Game", self.gameOverBox.ActionRole)
        self.gameOverBoxButton2.clicked.connect(self.exit_game)

        self.setWindowTitle("Snake Game")
        self.setStyleSheet("background: #333")

        self.board = Board(self)
        self.board.setStyleSheet("background: #fff;")

        self.mainLayout.addWidget(self.board)
        self.mainLayout.addWidget(self.statusbar)

        self.setLayout(self.mainLayout)
        self.show()

    # Reset method, it is called by game over box
    def restart_game(self):
        self.board.restartGame()

    # Exit method, it is called by game over box
    def exit_game(self):
        sys.exit()


"""
@ Game board class
"""


class Board(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.startGame()

    def startGame(self):
        # GET FOCUS
        self.setFocusPolicy(Qt.StrongFocus)

        # INITILIAZE ALL MANAGERS
        self.snakeManager = self.SnakeManager(self)
        self.foodManager = self.FoodManager(self)
        self.uiManager = self.UIManager(self)
        self.levelManager = self.LevelManager(self)
        self.timerManager = self.TimerManager(self)

        # CREATE SNAKE
        self.snakeManager.createSnake()
        # DROP FOOD
        self.foodManager.dropFood()
        # START TIMERS
        self.timerManager.startTicks()

    def restartGame(self):
        self.uiManager.resetTable()
        self.timerManager.timerStopped = False
        self.startGame()

    def paintEvent(self, event):
        painter = QPainter(self)
        sizes = (self.contentsRect().width(), self.contentsRect().height())
        if self.uiManager.oldSizes != sizes:
            self.uiManager.oldSizes = sizes
            self.uiManager.calculateBoardSizes()

        for pos in self.foodManager.foods:
            self.drawSquare(painter, self.sanitizeCoords(pos[0]), self.sanitizeCoords(pos[1]), 0xeb34e1)

        for pos in self.snakeManager.snake:
            self.drawSquare(painter, self.sanitizeCoords(pos[0]), self.sanitizeCoords(pos[1]), 0xeb3231)

    def sanitizeCoords(self, coord):
        return coord * self.uiManager.pixelMultiplier

    def drawSquare(self, painter, x, y, color):
        color = QColor(color)
        painter.fillRect(x, y, self.uiManager.pixelMultiplier, self.uiManager.pixelMultiplier, color)

    def keyPressEvent(self, event):
        self.snakeManager.checkMovement(event.key())

    class SnakeManager:
        def __init__(self, parent):
            self.board = parent
            self.length = 5
            self.growSnake = False

        def createSnake(self):
            self.direction = random.randint(1, 4)
            tiles = self.board.levelManager.tileCount
            startPosX = random.randint(int(tiles / 8), int(7 * tiles / 8))
            startPosY = random.randint(int(tiles / 8), int(7 * tiles / 8))
            self.snake = [(startPosX, startPosY)]
            i = False
            while i is False:
                # 1 up, 2 down, 3 stay still
                direction = random.randint(1, 5)
                upOrDown = random.randint(1, 3)
                nextCoordX = self.snake[-1][0]
                nextCoordY = self.snake[-1][1]
                if self.direction == 1 and direction == 1:
                    nextCoordX -= 1
                elif self.direction == 2 and direction == 2:
                    nextCoordY -= 1
                elif self.direction == 3 and direction == 3:
                    nextCoordY += 1
                elif self.direction == 4 and direction == 4:
                    nextCoordX += 1
                else:
                    if upOrDown == 1:
                        nextCoordY -= 1
                    elif upOrDown == 2:
                        nextCoordY += 1
                if (nextCoordX, nextCoordY) not in self.snake:
                    self.snake.append((nextCoordX, nextCoordY))
                if len(self.snake) == self.length:
                    i = True
            self.headX = self.snake[0][0]
            self.headY = self.snake[0][1]

        def checkMovement(self, key):
            if (self.direction == 1 and key == Qt.Key_Left) or (self.direction == 4 and key == Qt.Key_Right):
                return
            elif (self.direction == 3 and key == Qt.Key_Down) or (self.direction == 2 and key == Qt.Key_Up):
                return
            elif key == Qt.Key_Right:
                self.direction = 1
            elif key == Qt.Key_Down:
                self.direction = 2
            elif key == Qt.Key_Up:
                self.direction = 3
            elif key == Qt.Key_Left:
                self.direction = 4

        def moveSnake(self):
            self.headX = 0 if self.direction == 1 and self.headX + 1 == self.board.levelManager.tileCount else self.headX + 1 if self.direction == 1 else self.headX
            self.headX = self.board.levelManager.tileCount - 1 if self.direction == 4 and self.headX - 1 < 0 else self.headX - 1 if self.direction == 4 else self.headX
            self.headY = 0 if self.direction == 2 and self.headY + 1 == self.board.levelManager.tileCount else self.headY + 1 if self.direction == 2 else self.headY
            self.headY = self.board.levelManager.tileCount - 1 if self.direction == 3 and self.headY - 1 < 0 else self.headY - 1 if self.direction == 3 else self.headY
            self.snake.insert(0, (self.headX, self.headY))
            self.board.levelManager.endGame() if [x for x in self.snake[1:] if
                                                  x == (self.headX, self.headY)] != [] else None
            self.snake.pop() if self.growSnake == False else exec("self.growSnake = False")

        def checkFoodCollision(self):
            if (self.headX, self.headY, 0) in self.board.foodManager.foods:
                self.board.levelManager.points += 1
                self.board.uiManager.updatePointsText()
                self.growSnake = True
                self.board.foodManager.foods.remove((self.headX, self.headY, 0))
                self.board.foodManager.dropFood()
            elif (self.headX, self.headY, 1) in self.board.foodManager.foods:
                self.board.levelManager.points += 5
                self.board.uiManager.updatePointsText()
                self.board.foodManager.special = False
                self.board.foodManager.foods.remove((self.headX, self.headY, 1))

    class FoodManager:
        def __init__(self, parent):
            self.board = parent
            self.foods = []
            self.special = False

        def dropFood(self, foodType=0):
            tiles = self.board.levelManager.tileCount
            x = random.randint(0, tiles)
            y = random.randint(0, tiles)
            if (x, y) in self.board.snakeManager.snake:
                self.dropFood(foodType)
            else:
                self.special = True if foodType != 0 else False
                self.foods.append((x, y, foodType))

    class TimerManager:
        def __init__(self, parent):
            self.board = parent

            self.speed = 60
            self.timerStopped = False

            self.gameTicks = QTimer()
            self.gameTicks.timeout.connect(self.tickTock)

            self.clockTimer = QTimer()
            self.clockTimer.timeout.connect(self.updateElapsedTime)
            self.elapsedTime = QTime(00, 00)

        def updateElapsedTime(self):
            if self.timerStopped is False:
                self.elapsedTime = self.elapsedTime.addSecs(1)
                self.board.uiManager.updateTimerText()
                if self.board.foodManager.special is False:
                    foodChance = random.randint(1, 100)
                    if foodChance > 90:
                        self.board.foodManager.dropFood(1)

        def startTicks(self):
            self.clockTimer.start(1000)
            self.gameTicks.start(self.speed)
            self.board.update()

        def tickTock(self):
            if self.timerStopped is False:
                self.board.snakeManager.moveSnake()
                self.board.snakeManager.checkFoodCollision()
                self.board.levelManager.checkNextLevel()
                self.board.update()

        def resetTimers(self):
            self.elapsedTime = QTime(00, 00)

    class LevelManager:
        tileCount = 40

        def __init__(self, parent):
            self.board = parent
            self.points = 0
            self.level = 1
            self.requiredPoints = 5
            self.levelGeometryMultiplies = 5

        def endGame(self):
            self.board.timerManager.timerStopped = True
            self.board.uiManager.showGameOverBox()

        def checkNextLevel(self):
            if self.points >= self.requiredPoints:
                self.requiredPoints = math.floor((2 * self.requiredPoints) - (self.requiredPoints / 2))
                self.level += 1
                self.board.uiManager.updateLevelText()
                self.board.uiManager.updatePointsText()
                if self.level % self.levelGeometryMultiplies == 0:
                    self.tileCount += self.level
                    self.board.uiManager.calculateBoardSizes()

    class UIManager:
        pixelMultiplier = 8
        oldSizes = ()

        def __init__(self, parent):
            self.board = parent

        def calculateBoardSizes(self):
            edge = (self.board.levelManager.tileCount * self.pixelMultiplier)
            self.board.setFixedSize(edge, edge)

        def updateTimerText(self):
            window.timeLabel.setText(
                self.board.timerManager.elapsedTime.toString("mm:ss"))

        def updatePointsText(self):
            window.pointsLabel.setText(
                f"{str(self.board.levelManager.points)}/{str(self.board.levelManager.requiredPoints)}")

        def updateLevelText(self):
            window.levelLabel.setText(str(self.board.levelManager.level))

        def showGameOverBox(self):
            window.gameOverBox.setText(
                f"Elapsed time: {window.timeLabel.text()}\nPoints: {window.pointsLabel.text()}\nLevel: {window.levelLabel.text()}\n")
            window.gameOverBox.exec()

        def resetTable(self):
            window.pointsLabel.setText("0/5")
            window.levelLabel.setText("1")
            window.timeLabel.setText("00:00")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
