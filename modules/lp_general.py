'''#moxePy - A place to store MoxePython functions that have general usability across modules, but aren't necessarily specific to any one module'''
#pylint: disable=line-too-long
import csv
from pathlib import Path
import logging
from distutils.util import strtobool
from legopython import lp_logging #import this until we're able to fully deprecate the writeToFileLedger function

logger = logging.getLogger("moxepython")

def listdir_path_v2(file) :
    '''
    listdir_path_v2 - Given an input of file, directory, or file glob, return a generator of path objects with their relative paths (excluding directories).
        This v2 function returns a generator to control resource consumption when dealing with larger sets of files in a directory
        file - The file/directory/glob to use in creating the list
    '''
    fpath = Path(file)
    if fpath.is_dir() :
        logger.debug("file is a directory")
        yield from [ f for f in fpath.iterdir() if f.is_file() ] #[thing-to-output <other for/if/etc statements>]
    #If file is a file, load just that file into the list
    elif fpath.is_file() :
        logger.debug("file is a single file")
        yield fpath
    #If both is_dir and is_file are false, assume this is a glob (even though it could be a socket/block device/etc)
    else :
        logger.debug("file is neither file or directory, assuming fileglob")
        yield from [ f for f in Path(fpath.parent).glob(fpath.name) if f.is_file() ]


def yesno(question, default='no') :
    if default == 'yes' :
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        prompt = ' [y/n] '

    while True :
        try:
            resp = input(question + prompt).strip().lower()
            if default is not None and resp == '' :
                return default == 'yes'
            else:
                return bool(strtobool(resp))
        except ValueError:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def prompt_user_int(question: str, maximum:int, minimum:int = 0) -> int:
    ''' prompt user for {question} for INT response between {maximum} and {minimum} '''
    while True :
        try:
            user_response = input(f'{question}: ({minimum}-{maximum})  ')
            if user_response.lower() in ('exit','quit'):
                print('\nExiting')
                exit()
            #Converting response to int post check for 'exit' or 'quit' for graceful handling of user request.
            user_response = int(user_response)
            if minimum <= user_response <= maximum:
                return user_response
            else:
                print(f"\nPlease respond with an integer between {minimum} and {maximum}. Or, Ctrl+C to exit. \n")
        except ValueError:
            print(f"\nPlease respond with an integer between {minimum} and {maximum}. Or, Ctrl+C to exit. \n")
        except KeyboardInterrupt:
            print('\nCtrl+C detected, Exiting')
            exit()


def read_csv(filename: str, hasheader:bool = False) -> list:
    '''read a 1 column csv without headers from file, return list.
    hasheader = True removes the first line.
    '''
    try:
        with open(filename, newline='') as writer:
            reader = csv.reader(writer)
            if hasheader:
                reader.pop(0)
            csv_column = list(reader)
    except:
        print(f'{filename} not found, no data loaded.')
        return []
    return [item for sublist in csv_column for item in sublist]
