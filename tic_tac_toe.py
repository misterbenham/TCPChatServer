import sys


class TicTacToe:
    def __init__(self, turn):
        self.turn = turn
        self.count = 0
        self.gameOver = False
        self.theBoard = {}
        self.setupNewBoard()

    def setupNewBoard(self):
        self.theBoard = {'7': ' ', '8': ' ', '9': ' ',
                         '4': ' ', '5': ' ', '6': ' ',
                         '1': ' ', '2': ' ', '3': ' '}

    def setupNewGame(self, turn):
        self.turn = turn
        self.count = 0
        self.gameOver = False
        self.setupNewBoard()

    @staticmethod
    def printBoard(board):
        print(f"{board['7']}{'|'}{board['8']}{'|'}{board['9']}")
        print('-+-+-')
        print(f"{board['4']}{'|'}{board['5']}{'|'}{board['6']}")
        print('-+-+-')
        print(f"{board['1']}{'|'}{board['2']}{'|'}{board['3']}")

    @staticmethod
    def printHelpBoard():
        print("Use the NumPad to select the space you want...")
        print()
        print('7|8|9')
        print('-+-+-')
        print('4|5|6')
        print('-+-+-')
        print('1|2|3')
        print()

    def game(self):
        while True:
            while not self.gameOver:
                self.printHelpBoard()

                print(f"It's your turn, {self.turn}. Move to which place?: \n")
                self.printBoard(self.theBoard)
                move = input()

                while self.theBoard[move] != ' ':
                    print("Place already filled!\nMove to which place?")
                    move = input()

                self.theBoard[move] = self.turn
                self.count += 1
                print(f"Count is: {self.count}")

                if self.count >= 5:
                    space_list = [['7', '8', '9'], ['4', '5', '6'], ['1', '2', '3'], ['1', '4', '7'],
                                  ['2', '5', '8'], ['3', '6', '9'], ['1', '5', '9'], ['3', '5', '7']]

                    for win in space_list:
                        if self.theBoard[win[0]] == self.theBoard[win[1]] == self.theBoard[win[2]] != ' ':
                            self.printBoard(self.theBoard)
                            print("\nGame Over!")
                            print(f"{self.turn} won!")
                            self.gameOver = True
                            break

                    if self.count == 9 and not self.gameOver:
                        self.printBoard(self.theBoard)
                        print("\nGame Over!")
                        print("It's a tie!")
                        self.gameOver = True

                if self.turn == 'X':
                    self.turn = 'O'
                else:
                    self.turn = 'X'

            restart = input("Would you like to play again?: \n")
            if restart == 'yes':
                self.setupNewGame(self.turn)
            else:
                break


ttt = TicTacToe(turn='X')
ttt.game()
