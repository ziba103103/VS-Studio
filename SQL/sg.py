import logging
logging.basicConfig(level=logging.DEBUG)
# Настройка основного логгера
logging.basicConfig(
    filename='example.log',                # Название файла журнала
    filemode='w',                          # Режим открытия файла (перезаписывать файл)
    encoding='utf-8',                      # Указываем кодировку UTF-8
    level=logging.DEBUG                   # Укажите нужный вам уровень логирования
)

# Создание объекта logger
logger = logging.getLogger()

# Примеры логирования
logger.debug('Debug message')              # Сообщение уровня debug
logger.info('Info message')               # Информационное сообщение
logger.warning('Warning message')         # Предупреждающее сообщение
logger.error('Error message')             # Сообщение об ошибке
logger.critical('Critical message')       # Критическое сообщение

