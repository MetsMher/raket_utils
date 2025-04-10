import logging

from rich.logging import RichHandler

# Настройка логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Обработчик для вывода в консоль с использованием rich
console_handler = RichHandler(markup=True)
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

# Обработчик для записи в файл без rich
file_handler = logging.FileHandler(filename='log.txt', mode='a', encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
