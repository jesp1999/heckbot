from datetime import datetime

from colorama import Fore, Style

PRIMARY_GUILD_ID = 334491082241081347

WELCOME_CHANNEL_ID = 744611387371683962
ADMIN_CONSOLE_CHANNEL_ID = 744611387371683962

BOT_CUSTOM_STATUS = 'the part :)'

BOT_COMMAND_PREFIX = '!'

EMBED_COLOR = 0x040273

GUILD_JOIN_TITLE = ''
GUILD_JOIN_DESCRIPTION = ''


# TODO modify this and use in a logger
def CONSOLE_INFO_FMT():
    return (f'{Fore.BLUE}{datetime.now().strftime("%H:%M:%S")}{Fore.RESET} '
            f'{Style.BRIGHT}[{Fore.BLUE}INFO{Fore.RESET}]{Style.RESET_ALL}')
