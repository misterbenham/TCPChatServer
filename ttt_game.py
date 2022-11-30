import json

import utility


class TicTacToe:
    def __init__(self):
        self.turn = None
        self.count = 0
        self.move = None
        self.game_over = False
        self.the_board = {}
        self.setup_new_board()

    def setup_new_board(self):
        self.the_board = {'7': ' ', '8': ' ', '9': ' ',
                         '4': ' ', '5': ' ', '6': ' ',
                         '1': ' ', '2': ' ', '3': ' '}

    def setup_new_game(self, turn, move):
        self.turn = turn
        self.count = 0
        self.move = move
        self.game_over = False
        self.setup_new_board()

    @staticmethod
    def get_help_board():
        return "Use the NumPad to select the space you want...\n" \
               "\n" \
               "7|8|9\n" \
               "-+-+-\n" \
               "4|5|6\n" \
               "-+-+-\n" \
               "1|2|3\n"

    @staticmethod
    def get_board(board: dict) -> str:
        return f"{board['7']}{'|'}{board['8']}{'|'}{board['9']}\n" \
               f"-+-+-\n" \
               f"{board['4']}{'|'}{board['5']}{'|'}{board['6']}\n" \
               f"-+-+-\n" \
               f"{board['1']}{'|'}{board['2']}{'|'}{board['3']}"

    def updateBoard(self, the_board, turn, move):
        if the_board[move] != ' ':
            return 'Space already filled!', turn
        else:
            the_board[move] = turn
            self.count += 1

            if self.count >= 5:
                space_list = [['7', '8', '9'], ['4', '5', '6'], ['1', '2', '3'], ['1', '4', '7'],
                              ['2', '5', '8'], ['3', '6', '9'], ['1', '5', '9'], ['3', '5', '7']]

                for win in space_list:
                    if the_board[win[0]] == the_board[win[1]] == the_board[win[2]] != ' ':
                        self.game_over = True
                        return f"\nGame Over!\n{turn} won!", turn

                if self.count == 9 and not self.game_over:
                    self.game_over = True
                    return "\nGame Over!\nIt's a tie!", turn

        return the_board, turn
