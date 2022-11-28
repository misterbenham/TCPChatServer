import json

import utility


class TicTacToe:
    def __init__(self):
        self.turn = None
        self.count = 0
        self.move = None
        self.gameOver = False
        self.theBoard = {}
        self.setupNewBoard()

    def setupNewBoard(self):
        self.theBoard = {'7': ' ', '8': ' ', '9': ' ',
                         '4': ' ', '5': ' ', '6': ' ',
                         '1': ' ', '2': ' ', '3': ' '}

    def setupNewGame(self, turn, move):
        self.turn = turn
        self.count = 0
        self.move = move
        self.gameOver = False
        self.setupNewBoard()

    @staticmethod
    def getHelpBoard():
        return "Use the NumPad to select the space you want...\n" \
               "\n" \
               "7|8|9\n" \
               "-+-+-\n" \
               "4|5|6\n" \
               "-+-+-\n" \
               "1|2|3\n"

    @staticmethod
    def getBoard(board: dict) -> str:
        return f"{board['7']}{'|'}{board['8']}{'|'}{board['9']}\n" \
               f"-+-+-\n" \
               f"{board['4']}{'|'}{board['5']}{'|'}{board['6']}\n" \
               f"-+-+-\n" \
               f"{board['1']}{'|'}{board['2']}{'|'}{board['3']}"

    def updateBoard(self, theBoard, turn, move):
        if theBoard[move] != ' ':
            return 'Space already filled!', turn
        else:
            theBoard[move] = turn
            self.count += 1

            if self.count >= 5:
                space_list = [['7', '8', '9'], ['4', '5', '6'], ['1', '2', '3'], ['1', '4', '7'],
                              ['2', '5', '8'], ['3', '6', '9'], ['1', '5', '9'], ['3', '5', '7']]

                for win in space_list:
                    if theBoard[win[0]] == theBoard[win[1]] == theBoard[win[2]] != ' ':
                        self.gameOver = True
                        return f"\nGame Over!\n{turn} won!", turn

                if self.count == 9 and not self.gameOver:
                    self.gameOver = True
                    return "\nGame Over!\nIt's a tie!", turn

        return theBoard, turn
