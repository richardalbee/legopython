#pylint: disable=line-too-long
'''
    legoPython functions related to logging or logging-adjacent needs
'''
import sys
import time
from pathlib import Path
import json
import logging

logger = logging.getLogger("legopython")

def MPAddHandler(level=logging.INFO):
    '''
    Add the "default" handler for the legopython logger at the INFO level
    Pass a different log level in for different screen outputs
    '''
    ch = logging.StreamHandler(sys.stdout) #push log messages to the console
    ch.setFormatter(logging.Formatter('%(message)s')) #just show messages, not module or time
    ch.setLevel(level)
    logger.addHandler(ch)

    if level == logging.DEBUG : #this sets up other debugging functionality
        MPDebugLogging()

def MPDebugLogging():
    '''
    Function to adjust the to a debug level
    NOTE -> This assumes a handler already exists, and hasn't been cleared
    '''
    logger.handlers[0].setLevel(logging.DEBUG) #We control this logger, and only have 1 handler set
    logger.handlers[0].setFormatter(logging.Formatter('%(levelname)-8s: %(module)s:%(funcName)s: %(message)s'))

def clearMPDefaultHandler():
    '''
    Remove handlers from the logger, needed for scripts that intend to log to files or
    manage logging in their own logger.
    WARNING: Calling this without setting up additional handlers results in almost all logging going nowhere
    '''
    logger.removeHandler(logger.handlers[0]) #This seems safer than logger.handlers.clear()

def testLPLogging():
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

def writeToFileLedger(filename,sourcepath,destpath,receivetime,filesize,fileledgerpath='.') :
    '''
    Replicate the file ledger functionality originally present in S3same
    '''
    fileledgertimestamp = '%Y-%m-%d %H:%M:%S%z'
    # prep file
    ledgerfile = Path(fileledgerpath, 's3same-fileledger-' + time.strftime('%Y-%m-%d') + '.json')
    if not ledgerfile.is_file() :
        with open(ledgerfile, 'a') as file :
            pass
    logentry = {
        'TransferTime': time.strftime(fileledgertimestamp),
        'FileName': str(filename),
        'SourcePath': str(sourcepath),
        'DestPath': str(destpath),
        'ReceiveTime': time.strftime(fileledgertimestamp, time.gmtime(receivetime)),
        'FileSize': str(filesize)
    }
    logger.debug(f'ledgerfile: {ledgerfile}|logentry: {logentry}')
    with open(ledgerfile, 'a') as f:
        f.write(json.dumps(logentry) + '\n')
