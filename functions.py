import os
from datetime import datetime


class Log:

    def __init__(self, bot_directory, filename=None):
        self.filename = filename
        self.bot_directory = bot_directory

    def _write(self, message, color, nivel, end='\n', flush=False):
        try:
            print(color + message + '\033[0m', end=end, flush=flush)
            if self.filename:
                date = datetime.now().strftime("%Y%m%d")
                times = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                if not os.path.exists(f'{self.bot_directory}/logs'):
                    os.makedirs(f'{self.bot_directory}logs')
                with open(f"{self.bot_directory}logs/{self.filename}_{date}.log", 'a') as file:
                    file.write(f"{times} | {nivel} | {message} \n")
        except Exception as e:
            print(e)

    def debug(self, message, end='\n', flush=False):
        color = '\033[37m'
        nivel = 'DEBUG'
        self._write(message, color, nivel, end=end, flush=flush)

    def error(self, message, end='\n', flush=False):
        color = '\033[31m'
        nivel = 'CRITICAL'
        self._write(message, color, nivel, end=end, flush=flush)

    def alert(self, message, end='\n', flush=False):
        color = '\033[35m'
        nivel = 'ERROR'
        self._write(message, color, nivel, end=end, flush=flush)

    def warning(self, message, end='\n', flush=False):
        color = '\033[33m'
        nivel = 'WARNING'
        self._write(message, color, nivel, end=end, flush=flush)

    def info(self, message, end='\n', flush=False):
        color = '\033[34m'
        nivel = 'INFO'
        self._write(message, color, nivel, end=end, flush=flush)

    def data(self, message, end='\n', flush=False):
        color = '\033[36m'
        nivel = 'DATA'
        self._write(message, color, nivel, end=end, flush=flush)

    def success(self, message, end='\n', flush=False):
        color = '\033[32m'
        nivel = 'SUCCESS'
        self._write(message, color, nivel, end=end, flush=flush)


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
