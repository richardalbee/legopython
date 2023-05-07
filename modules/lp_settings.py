'''Global Settings for toolsPython

To add a new setting, initialize the global variable to the default.
Then, add entry into tools_settings_dict
Last, add logic to cache the variable in __configparse_get_cache
'''
import sys
from configparser import ConfigParser
from pathlib import Path
from legopython import lp_logging, lp_general

ENVIRONMENT = 'test'
LOGGER_LEVEL = "none"

tools_settings_dict = {
    "Environment" : {'config_section_name':'Global','variable_name': "Environment", 'variable_value':ENVIRONMENT, 'allowed_values': ['prod', 'qa', 'test', 'int','demo']},
    "Logger_Level" : {'config_section_name':'Global','variable_name': "Logger_Level", 'variable_value':LOGGER_LEVEL, 'allowed_values': ['none', 'info', 'debug']}
    }

tools_folder = Path.home().joinpath(".pythontools")
config_filepath = tools_folder.joinpath("toolspython_settings.ini")
pip_credentials_filepath = Path.home().joinpath(".netrc")


def __configparse_get_cache() -> bool:
    """Private function to get environment stored on disk

    Return true if the file exists in proper format
    return false if file missing or invalid format
    """
    global ENVIRONMENT
    global LOGGER_LEVEL

    config = ConfigParser()
    if not config_filepath.exists():
        lp_logging.debug("Could not find cached environment file at %s", config_filepath)
        return False
    config.read(config_filepath)

    if config.has_option('Global', 'Environment'): #Copy this structure for a new variable
        ENVIRONMENT = config.get('Global', 'Environment')
    else:
        lp_logging.error("Corrupted or invalid settings file found at %s.", config_filepath)
        return False

    if config.has_option('Global', 'Logger_Level'):
        LOGGER_LEVEL = config.get('Global', 'Logger_Level')
    else:
        lp_logging.error("Corrupted or invalid settings file found at %s.", config_filepath)
        return False
    #by getting this far all config values were pulled properly.
    return True


def _configparse_cache():
    """Private function to store environment on disk"""
    tools_folder.mkdir(exist_ok=True)
    config = ConfigParser()

    for key,value in tools_settings_dict.items():
        #If the section does not exist, create it
        if not config.has_section(value['config_section_name']):
            config.add_section(value['config_section_name'])
        print(value['config_section_name'], value['variable_name'], value['variable_value'])
        config.set(value['config_section_name'], value['variable_name'], value['variable_value'])

    with open(config_filepath, 'w') as configfile:    # save
        config.write(configfile)


def set_environment(env:str):
    '''Callable function for setting the global environment variable.'''

    #Since a dictionary is not auto updated by the global variable, updating dict
    if env.lower() in tools_settings_dict['Environment']['allowed_values']:
        tools_settings_dict['Environment']['variable_value']=env.lower()
        _configparse_cache()
    else:
        lp_logging.error(f'Supported Environments are: {tools_settings_dict["Environment"]["allowed_values"]}')
        return

    #Force user to exit to ensure new environment variable is pulled by all modules.
    lp_logging.info('Exiting session to force toolsPython to pull latest environment on restart.')
    sys.exit()

def create_pip_update_credentials():
    '''Creates .netrc file for updating user toolsPython install in home dir.'''
    artifactory_serviceaccount_pw = lp_general.get_secret_v2(secret_name='pypi-artifactory-token')
    with open('.netrc', 'w', newline='') as newfile:
        newfile.write('machine toolshealth.jfrog.io\n')
        newfile.write('login pypi-user\n')
        newfile.write(f'password {artifactory_serviceaccount_pw}') #value needs to be API key

#Set Environment variable from file, else create config file if does not exist.
if __configparse_get_cache():
    lp_logging.debug(f"Successfully loaded file from {config_filepath}")
else:
    _configparse_cache()
    lp_logging.debug(f"{config_filepath} created with ENV set to: {ENVIRONMENT} and logger_level set to {LOGGER_LEVEL}")
lp_logging.debug(f"Environment is set to {ENVIRONMENT}.")

if not pip_credentials_filepath.exists():
    create_pip_update_credentials()
