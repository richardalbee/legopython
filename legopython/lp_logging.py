#pylint: disable=line-too-long
'''
Module dedicated to handling how python logs https://docs.python.org/3/howto/logging.html

LOG LEVELS:
NOTSET
DEBUG
INFO
WARNING
ERROR
CRITICAL
'''
import sys
import logging
from legopython import lp_settings

logger = logging.getLogger("legopython")

def __console_log_handler(level=logger.info):
    '''
    Add the "default" handler for the moxepython logger at the INFO level
    Pass a different log level in for different screen outputs
    '''
    console_config = logging.StreamHandler(sys.stdout) #push log messages to the console
    console_config.setFormatter(logging.Formatter('%(message)s')) #just show messages, not module or time
    console_config.setLevel(level)
    logger.addHandler(console_config)

    if level == logging.DEBUG : #Enable timestamps and showing debug statements if logger set to debug
        logger.handlers[0].setLevel(logging.DEBUG) #We control this logger, and only have 1 handler set
        logger.handlers[0].setFormatter(logging.Formatter('%(levelname)-8s: %(module)s:%(funcName)s: %(message)s'))


def __test_logging():
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')


def main():
    '''Configures log file settings and user experience of console print outs'''

    #Make logger.{type} print to console like normal prints
    __console_log_handler(lp_settings.LOGGER_LEVEL.upper())

    #Configure how the log file is set up if enabled.
    if lp_settings.LOG_FILE_ENABLED:
        #This controls where logger.{type} is printed to and formatting
        logging.basicConfig(
            filename = f'{lp_settings.LOG_LOCATION}/log.txt',
            encoding ='utf-8',
            level = lp_settings.LOGGER_LEVEL.upper(),
            format = '%(asctime)s;%(levelname)s;%(message)s',
            datefmt ='%Y-%m-%d %H:%M:%S'
            )

    __test_logging()

if __name__ == '__main__':
    main()
