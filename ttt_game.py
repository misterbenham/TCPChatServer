import json

import utility


def return_new_board():
    return {'7': ' ', '8': ' ', '9': ' ',
                      '4': ' ', '5': ' ', '6': ' ',
                      '1': ' ', '2': ' ', '3': ' '}


def get_help_board():
    return "Use the NumPad to select the space you want...\n" \
           "\n" \
           "7|8|9\n" \
           "-+-+-\n" \
           "4|5|6\n" \
           "-+-+-\n" \
           "1|2|3\n"


def get_board(board: dict) -> str:
    return f"{board['7']}{'|'}{board['8']}{'|'}{board['9']}\n" \
           f"-+-+-\n" \
           f"{board['4']}{'|'}{board['5']}{'|'}{board['6']}\n" \
           f"-+-+-\n" \
           f"{board['1']}{'|'}{board['2']}{'|'}{board['3']}"


def updateBoard(the_board, turn, move):
    game_over = False
    if the_board[move] != ' ':
        return 'Space already filled!', turn
    else:
        the_board[move] = turn
        space_list = [['7', '8', '9'], ['4', '5', '6'], ['1', '2', '3'], ['1', '4', '7'],
                      ['2', '5', '8'], ['3', '6', '9'], ['1', '5', '9'], ['3', '5', '7']]

        for win in space_list:
            if the_board[win[0]] == the_board[win[1]] == the_board[win[2]] != ' ':
                game_over = True
                the_board = "won"
                return the_board, turn

        if not game_over:
            for i in range(1, 9):
                if the_board[str(i)] == " ":
                    break
            else:
                game_over = True
                the_board = "tie"

            return the_board, turn

    return the_board, turn
