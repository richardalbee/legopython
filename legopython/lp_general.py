'''A place to store legoPython functions that have general usability across modules, but aren't necessarily specific to any one module'''
#pylint: disable=line-too-long
import csv
from pathlib import Path
import logging
from distutils.util import strtobool

logger = logging.getLogger("legopython")

def listdir_path(file:str) :
    '''
    Given an input of file, directory, or file glob, return a generator of path objects with their relative paths (excluding directories).
        returns a generator to control resource consumption when dealing with larger sets of files in a directory
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


def prompt_user_yesno(question, default='no') :
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
        with open(filename, newline='', encoding='utf-8') as writer:
            reader = csv.reader(writer)
            if hasheader:
                reader.pop(0)
            csv_column = list(reader)
    except OSError:
        print(f'{filename} not found, no data loaded.')
        return []
    return [item for sublist in csv_column for item in sublist]


tools_settings_dict = {
    "Environment" : {'config_section_name':'Global','variable_name': "Environment", 'variable_value': '', 'allowed_values': ['prod', 'test']},
    "Logger_Level" : {'config_section_name':'Global','variable_name': "Logger_Level", 'variable_value': '', 'allowed_values': ['none', 'info', 'debug']},
    "AWS_Region" : {'config_section_name':'Global','variable_name': "AWS_Region", 'variable_value': '', 'allowed_values': ['us-east-2','us-east-1','us-west-1','us-west-2','af-south-1','ap-east-1','ap-south-2','ap-southeast-3','ap-southeast-4','ap-south-1','ap-northeast-3','ap-northeast-2','ap-southeast-1','ap-southeast-2','ap-northeast-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-south-1','eu-west-3','eu-north-1','eu-central-2','me-south-1','me-central-1','sa-east-1','us-gov-east-1','us-gov-west-1']}
    }


result = [x['variable_name'] for x in tools_settings_dict.values()]
print(result)
#for config_section in list(set([x['variable_name'] for x in tools_settings_dict.values()])):
    #print(config_section)


for key in tools_settings_dict:
    print(tools_settings_dict[key])
    print(tools_settings_dict[key]['config_section_name'])
    break