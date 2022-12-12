import enum


class LoginCommands(enum.Enum):
    """
    Enum Header values to be used for json packets.
    Values for login commands.
    """
    LOGIN = '1'
    REGISTER = '2'
    REGISTERED = '3'
    LOGGED_IN = '4'


class LoggedInCommands(enum.Enum):
    """
    Header values for logged in commands.
    """
    BROADCAST = '1'
    AUTHENTICATE_DIRECT_MESSAGE = '2'
    DIRECT_MESSAGE = '3'
    PRINT_DM = '4'
    ADD_FRIEND = '5'
    VIEW_FRIEND_REQUESTS = '6'
    VIEW_FRIENDS = '7'
    AUTH_TIC_TAC_TOE = '8'
    VIEW_TIC_TAC_TOE_REQUESTS = '9'
    SET_STATUS_AWAY = '10'
    HELP = '11'
    QUIT = '12'


class Responses(enum.Enum):
    """
    Header values for responses.
    """
    SUCCESS = '1'
    ERROR = '2'
    BROADCAST_MSG = '3'
    DM_ERROR = '4'
    PRINT_FRIEND_REQUESTS = '5'
    PRINT_FRIENDS_LIST = '6'
    PRINT_STATUS_AWAY = '7'
    PRINT_TTT_REQUESTS = '8'
    ONLINE_NOTIFICATION = '9'
    TIC_TAC_TOE_REQUEST = '10'
    TIC_TAC_TOE_CONFIRM = '11'
    TIC_TAC_TOE_DENY = '12'
    PLAY_TIC_TAC_TOE = '13'
    TIC_TAC_TOE_ERROR = '14'
    TIC_TAC_TOE_SPACE_ERROR = '15'
    TIC_TAC_TOE_WINNER = '16'
    TIC_TAC_TOE_TIE = '17'
