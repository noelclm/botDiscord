import os
import pytz
import discord
from datetime import datetime


class Log:

    def __init__(self, bot_directory, filename=None):
        self.tz = pytz.timezone(os.getenv('TIMEZONE'))
        self.filename = filename
        self.bot_directory = bot_directory

    def _write(self, function, message, color, nivel, end='\n', flush=False):
        try:
            date = datetime.now().strftime("%Y%m%d")
            times = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\033[1m\033[30m{times}\033[0m \033[1m{color}{nivel.ljust(8)}\033[0m "
                  f"\033[35mbot.{function}\033[0m {message}", end=end, flush=flush)
            if self.filename:
                if not os.path.exists(f'{self.bot_directory}/logs'):
                    os.makedirs(f'{self.bot_directory}logs')
                with open(f"{self.bot_directory}logs/{self.filename}_{date}.log", 'a') as file:
                    file.write(f"{times} {nivel.ljust(8)} bot.{function} {message}\n")
        except Exception as e:
            print(e)

    def debug(self, function, message, end='\n', flush=False):
        color = '\033[37m'
        nivel = 'DEBUG'
        self._write(function, message, color, nivel, end=end, flush=flush)

    def error(self, function, message, end='\n', flush=False):
        color = '\033[31m'
        nivel = 'CRITICAL'
        self._write(function, message, color, nivel, end=end, flush=flush)

    def alert(self, function, message, end='\n', flush=False):
        color = '\033[35m'
        nivel = 'ERROR'
        self._write(function, message, color, nivel, end=end, flush=flush)

    def warning(self, function, message, end='\n', flush=False):
        color = '\033[33m'
        nivel = 'WARNING'
        self._write(function, message, color, nivel, end=end, flush=flush)

    def info(self, function, message, end='\n', flush=False):
        color = '\033[34m'
        nivel = 'INFO'
        self._write(function, message, color, nivel, end=end, flush=flush)

    def data(self, function, message, end='\n', flush=False):
        color = '\033[36m'
        nivel = 'DATA'
        self._write(function, message, color, nivel, end=end, flush=flush)

    def success(self, function, message, end='\n', flush=False):
        color = '\033[32m'
        nivel = 'SUCCESS'
        self._write(function, message, color, nivel, end=end, flush=flush)


def split_message(message, max_length=2000):
    # Dividir el mensaje en partes de hasta max_length caracteres
    parts = []
    while len(message) > max_length:
        split_index = message.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(message[:split_index])
        message = message[split_index:].lstrip()
    parts.append(message)
    return parts

def text_state(state):
    if state == discord.Status.online or state == 'online':
        status_name = 'conectado'
    elif state == discord.Status.offline or state == 'offline':
        status_name = 'desconectado'
    elif state == discord.Status.idle or state == 'idle':
        status_name = 'ausente'
    elif state == discord.Status.dnd or state == 'dnd':
        status_name = 'no molestar'
    elif state == discord.Status.invisible or state == 'invisible':
        status_name = 'invisible'
    else:
        status_name = 'estado no registrado'
    return status_name
