'''Module Configuring how legoPython logs with global settings in lp_settings.
 https://docs.python.org/3/howto/logging.html

Console prints the lowest level set in lp_settings.LOGGER_LEVEL

0: NOTSET,
10: DEBUG
20: INFO
30: WARNING
40: ERROR
50: CRITICAL
'''
import sys
import logging
from legopython import lp_settings
logger = logging.getLogger("legopython")


def __console_log_handler(level=logger.info):
    '''Add the "default" handler at the INFO level'''
    console_config = logging.StreamHandler(sys.stdout) #push log messages to the console
    console_config.setFormatter(logging.Formatter('%(message)s')) #just show messages, not module or time
    console_config.setLevel(level)
    logger.addHandler(console_config)

    if level == logging.DEBUG : #Enable timestamps and showing debug statements if logger set to debug
        logger.handlers[0].setLevel(logging.DEBUG) #We control this logger, and only have 1 handler set
        logger.handlers[0].setFormatter(logging.Formatter('%(levelname)-8s: %(module)s:%(funcName)s: %(message)s'))


def __test_logging():
    print('print message')
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')


#Configures how console print outs through std.out'''
__console_log_handler(lp_settings.LOGGER_LEVEL.upper())

#This controls what logger.{type} is printed and how the log file is formatted.
if lp_settings.LOG_FILE_ENABLED:
    logging.basicConfig(
        filename = f'{lp_settings.LOG_LOCATION}/log.txt',
        encoding ='utf-8',
        level = lp_settings.LOGGER_LEVEL.upper(),
        format = '%(asctime)s;%(levelname)s;%(message)s',
        datefmt ='%Y-%m-%d %H:%M:%S'
        )
