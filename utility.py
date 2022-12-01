import enum


class LoginCommands(enum.Enum):
    """
    Enum Header values to be used for json packets.
    Values for login commands.
    """
    LOGIN = 'login'
    REGISTER = 'register'
    REGISTERED = 'registered'
    LOGGED_IN = 'logged_in'


class LoggedInCommands(enum.Enum):
    """
    Header values for logged in commands.
    """
    BROADCAST = 'broadcast'
    AUTHENTICATE_DIRECT_MESSAGE = 'dm'
    DIRECT_MESSAGE = 'direct_message'
    PRINT_DM = 'print_dm'
    ADD_FRIEND = 'af'
    VIEW_FRIEND_REQUESTS = 'fr'
    VIEW_FRIENDS = 'vf'
    AUTH_TIC_TAC_TOE = 'ttt'
    VIEW_TIC_TAC_TOE_REQUESTS = 'vttt'
    SET_STATUS_AWAY = 'ssa'
    HELP = 'help'
    QUIT = 'quit'


class Responses(enum.Enum):
    """
    Header values for responses.
    """
    SUCCESS = 'success'
    ERROR = 'error'
    BROADCAST_MSG = 'broadcast_msg'
    PRINT_FRIEND_REQUESTS = 'pfr'
    PRINT_FRIENDS_LIST = 'pfl'
    PRINT_STATUS_AWAY = 'ssa'
    PRINT_TTT_REQUESTS = 'ptr'
    ONLINE_NOTIFICATION = 'of'
    TIC_TAC_TOE_REQUEST = 'tttr'
    TIC_TAC_TOE_CONFIRM = 'tttc'
    TIC_TAC_TOE_DENY = 'tttd'
    PLAY_TIC_TAC_TOE = 'pttt'
    TIC_TAC_TOE_ERROR = 'ttte'
    TIC_TAC_TOE_SPACE_ERROR = 'Space already filled!'
