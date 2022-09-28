import enum


class LoginCommands(enum.Enum):
    LOGIN = 'login'
    REGISTER = 'register'
    LOGGED_IN = 'logged_in'


class LoggedInCommands(enum.Enum):
    BROADCAST = 'broadcast'
    DIRECT_MESSAGE = 'dm'
    HELP = 'help'
    QUIT = 'quit'


class Responses(enum.Enum):
    SUCCESS = 'success'
    ERROR = 'error'
    BROADCAST_MSG = 'broadcast_msg'

