import logging
'''
For all packages in legoPython, set up the moxepython logger to use
'''

def legoLoggingSetup():
    '''
    Set up the default moxepython logger. 
    '''
    #legoPython modules should log standardly at the INFO level instead of using print()
    logger = logging.getLogger("legopython")
    logger.setLevel(logging.DEBUG) #logger at DEBUG use handlers to control output level

legoLoggingSetup()
