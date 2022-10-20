import enum


class LoginCommands(enum.Enum):
    LOGIN = 'login'
    REGISTER = 'register'
    REGISTERED = 'registered'
    LOGGED_IN = 'logged_in'


class LoggedInCommands(enum.Enum):
    BROADCAST = 'broadcast'
    AUTHENTICATE_DIRECT_MESSAGE = 'dm'
    DIRECT_MESSAGE = 'direct_message'
    PRINT_DM = 'print_dm'
    HELP = 'help'
    QUIT = 'quit'


class Responses(enum.Enum):
    SUCCESS = 'success'
    ERROR = 'error'
    BROADCAST_MSG = 'broadcast_msg'

