'''Global Settings for legopython.

Lego Python supports the following

ENVIRONMENT: MoxeAPI and external module templates point different API endpoints depending on env.
LOGGER_LEVEL = Controls both console and log file logging levels in lp_logging
LOG_FILE_ENABLED = Boolean string for creating a log file.
LOG_LOCATION = Filepath to the log file.

To add a new setting:
1. create global variable.
2. add entry into settings_dict (alias must be unique)
3. add debug printout for new global in def main()
'''
import os
import sys
import logging
from configparser import ConfigParser
from pathlib import Path
logger = logging.getLogger("legopython")

#local globals
lp_folder = Path.home().joinpath(".lp")
config_filepath = lp_folder.joinpath("settings.ini")
pip_credentials_filepath = Path.home().joinpath(".netrc")

#GLOBAL SETTINGS: Initialized values if config file does not exist.
ENVIRONMENT = 'test'
LOGGER_LEVEL = 'debug'
LOG_FILE_ENABLED = 'false'
LOG_LOCATION = str(lp_folder)
AWS_REGION = 'us-east-2'

#Dictionary storing all configuration of global settings.
settings_dict = {
    "Environment" : {'section':'Global','name': "Environment", 'value': ENVIRONMENT, 'alias':['env','environment'], 'allowed_values': ['prod', 'test']},
    "AWS_Region" : {'section':'Global','name': "AWS_Region", 'value': AWS_REGION, 'alias':['aws', 'aws_region', 'region'], 'allowed_values': ['us-east-2','us-east-1','us-west-1','us-west-2']},
    "Log_File_Enabled" : {'section':'Logging','name': "Log_File_Enabled", 'value': LOG_FILE_ENABLED, 'alias':['log_file_enabled','log_enabled'], 'allowed_values': ['true','false']},
    "Log_Location" : {'section':'Logging','name': "Log_Location", 'value': LOG_LOCATION, 'alias':['log_file','log_location'], 'allowed_values': ['valid_path()_location_only']},
    "Logger_Level" : {'section':'Logging','name': "Logger_Level", 'value': LOGGER_LEVEL, 'alias':['logger_level', 'log_level'], 'allowed_values': ['notset', 'debug', 'info', 'warn', 'error', 'critical']}
    }


def __configparse_get_cache() -> bool:
    """Private function to get environment stored on disk

    Return true if the file exists in proper format
    return false if file missing or invalid format
    """
    global ENVIRONMENT, LOGGER_LEVEL, AWS_REGION, LOG_LOCATION, LOG_FILE_ENABLED

    config = ConfigParser()
    if not config_filepath.exists():
        print(f"Could not find cached environment file at {config_filepath}")
        return False
    config.read(config_filepath)

    for setting in settings_dict:
        if config.has_option(settings_dict[setting]['section'], settings_dict[setting]['name']):
            settings_dict[setting]['value'] = config.get(settings_dict[setting]['section'], settings_dict[setting]['name'])
        else:
            print(f"Invalid {settings_dict[setting]['name']} config setting found at {config_filepath}.")
            return False

    #Assign the globals values from cache
    ENVIRONMENT = settings_dict['Environment']['value']
    LOGGER_LEVEL = settings_dict['Logger_Level']['value']
    LOG_FILE_ENABLED = settings_dict['Log_File_Enabled']['value']
    LOG_LOCATION = settings_dict['Log_Location']['value']
    AWS_REGION = settings_dict['AWS_Region']['value']
    return True #Successfully imported settings file


def __configparse_cache():
    """Private function to save settings to disk"""
    lp_folder.mkdir(exist_ok=True)
    config = ConfigParser()

    #If the section does not exist, create it
    print('\nCaching new global setting values')
    for key, value in settings_dict.items():
        if not config.has_section(value['section']):
            config.add_section(value['section'])
        config.set(value['section'], value['name'], value['value']) #Create the setting file

    #Save config file
    with open(config_filepath, 'w', encoding='utf-8') as configfile:
        config.write(configfile)


def set_global_setting(setting_name:str, new_value:str) -> None:
    '''Update the value of a global setting. Exits after updating to ensure global propagates'''
    valid_aliases = []
    for setting in settings_dict:
        #check to see if a valid global name entered
        if setting_name in settings_dict[setting]['alias']:
            if new_value.lower() in settings_dict[setting]['allowed_values'] and setting_name.lower() != 'log_location':
                settings_dict[setting]['value']=new_value.lower()
                __configparse_cache()
                print('Exiting session to force new setting values to all modules')
                sys.exit()
            elif setting_name.lower() == 'log_location':
                if os.path.isdir(new_value):
                    settings_dict[setting]['value']=new_value.lower()
                    __configparse_cache()
                    print('Exiting session to force new setting values to all modules')
                    sys.exit()
                else:
                    print(f'{new_value} is not a valid path. Please provide a valid path.')
                    return
            else:
                print(f'Supported {setting} values: {settings_dict[setting]["allowed_values"]}')
                return
        valid_aliases.append(settings_dict[setting]['alias'])

    #Valid global name was not entered
    print(f'\n{setting_name} is not a valid setting name. Valid setting are: {valid_aliases}')


def __create_pip_update_credentials():
    '''Creates .netrc file for autoupdating legopython from artifactory.
    Used when publishing a pip internally if module is used at a secure workplace.

    #https://pip.pypa.io/en/stable/topics/authentication/'''
    #artifactory_serviceaccount_pw = lp_secretsmanager.get_secret_v2(secret_name='pypi-artifactory-token')
    with open('.netrc', 'w', newline='', encoding='utf-8') as newfile:
        newfile.write('machine toolshealth.jfrog.io\n')
        newfile.write('login pypi-user\n')
        #newfile.write(f'password {artifactory_serviceaccount_pw}') #value needs to be API key


#Settings file ran to initialize settings file to globals.
if __configparse_get_cache():
    logger.info(f"Successfully loaded file from {config_filepath}")
    logger.debug(f"{config_filepath} loaded: ENVIRONMENT={ENVIRONMENT}, LOG_FILE_ENABLED={LOG_FILE_ENABLED}, LOGGER_LEVEL={LOGGER_LEVEL}, LOG_LOCATION={LOG_LOCATION}")
else:
    #If settings file did not load, initialize/overwrite setting file with defaults.
    logger.debug(f"{config_filepath} created with defaults: ENVIRONMENT={ENVIRONMENT}, LOG_FILE_ENABLED={LOG_FILE_ENABLED}, LOGGER_LEVEL={LOGGER_LEVEL}, AWS_REGION={AWS_REGION}")
    __configparse_cache()
