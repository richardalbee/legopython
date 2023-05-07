'''legoPython logger setup'''
import logging

def logging_initialize():
    '''
    Set up the default moxepython logger. 
    '''
    #legoPython modules should log standardly at the INFO level instead of using print()
    logger = logging.getLogger("legopython")
    logger.setLevel(logging.DEBUG) #logger at DEBUG use handlers to control output level

logging_initialize()
