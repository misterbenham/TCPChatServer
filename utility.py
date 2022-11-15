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
    ONLINE_NOTIFICATION = 'of'
