#pylint: disable=line-too-long, consider-using-dict-items, no-value-for-parameter, logging-fstring-interpolation, global-statement
'''Global Settings for legopython

To add a new setting:
1. create global variable.
2. add entry into settings_dict (alias must be unique)
3. add debug printout for new global in def main()
TODO: Add support for non "global" section
'''
import sys
from configparser import ConfigParser
from pathlib import Path

#Initialized values if config file does not exist
ENVIRONMENT = 'test'
LOGGER_LEVEL = 'info'
AWS_REGION = 'us-east-2'

tools_folder = Path.home().joinpath(".lp")
config_filepath = tools_folder.joinpath("settings.ini")
pip_credentials_filepath = Path.home().joinpath(".netrc")

#dictionary storing all configuration of global settings
settings_dict = {
    "Environment" : {'section':'Global','name': "Environment", 'value': ENVIRONMENT, 'alias':['env','environment'], 'allowed_values': ['prod', 'test']},
    "Logger_Level" : {'section':'Global','name': "Logger_Level", 'value': LOGGER_LEVEL, 'alias':['log','logger','logger_level','logging'], 'allowed_values': ['notset', 'debug', 'info', 'warn', 'error', 'critical']},
    "AWS_Region" : {'section':'Global','name': "AWS_Region", 'value': AWS_REGION, 'alias':['aws', 'aws_region', 'region'], 'allowed_values': ['us-east-2','us-east-1','us-west-1','us-west-2','af-south-1','ap-east-1','ap-south-2','ap-southeast-3','ap-southeast-4','ap-south-1','ap-northeast-3','ap-northeast-2','ap-southeast-1','ap-southeast-2','ap-northeast-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-south-1','eu-west-3','eu-north-1','eu-central-2','me-south-1','me-central-1','sa-east-1','us-gov-east-1','us-gov-west-1']}
    }


def __configparse_get_cache() -> bool:
    """Private function to get environment stored on disk

    Return true if the file exists in proper format
    return false if file missing or invalid format
    """
    global ENVIRONMENT, LOGGER_LEVEL, AWS_REGION

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

    ENVIRONMENT = settings_dict['Environment']['value']
    LOGGER_LEVEL = settings_dict['Logger_Level']['value']
    AWS_REGION = settings_dict['AWS_Region']['value']
    return True #All config values properly read


def __configparse_cache():
    """Private function to save settings to disk"""
    tools_folder.mkdir(exist_ok=True)
    config = ConfigParser()

    #If the section does not exist, create it
    for key,value in settings_dict.items():
        if not config.has_section(value['section']):
            config.add_section(value['section'])
        print(value['section'], value['name'], value['value'])  #logger.debug
        config.set(value['section'], value['name'], value['value']) #Create the setting in settings file

    #Save config file
    with open(config_filepath, 'w', encoding='utf-8') as configfile:
        config.write(configfile)


def set_global_setting(global_name:str, new_value:str) -> None:
    '''Update the value of a global setting. Exits after updating to ensure global propagates'''

    #Since a dictionary is not auto updated by the global variable, updating dict
    valid_aliases = []
    for setting in settings_dict:
        #check to see if a valid global name entered
        if global_name in settings_dict[setting]['alias']:
            if new_value.lower() in settings_dict[setting]['allowed_values']:
                settings_dict[setting]['value']=new_value.lower()
                __configparse_cache()
                print('Exiting session to force new setting values to all modules')
                sys.exit()
            else:
                print(f'Supported {setting} values: {settings_dict[setting]["allowed_values"]}')
                return
        valid_aliases.append(settings_dict[setting]['alias'])

    #Valid global name was not entered
    print(f'\n{global_name} is not a setting. Valid setting are: {valid_aliases}')


def __create_pip_update_credentials():
    '''Creates .netrc file for autoupdating legopython from artifactory.
    Used when publishing a pip internally if module is used at a secure workplace.

    #https://pip.pypa.io/en/stable/topics/authentication/'''
    #artifactory_serviceaccount_pw = lp_secretsmanager.get_secret_v2(secret_name='pypi-artifactory-token')
    with open('.netrc', 'w', newline='', encoding='utf-8') as newfile:
        newfile.write('machine toolshealth.jfrog.io\n')
        newfile.write('login pypi-user\n')
        #newfile.write(f'password {artifactory_serviceaccount_pw}') #value needs to be API key


def main():
    '''
    Settings file ran to initialize settings file to globals
    '''
    #Check if there is a valid settings file.
    if __configparse_get_cache():
        print(f"Successfully loaded file from {config_filepath}")
    else:
        #If settings file did not load, initialize/overwrite setting file with defaults.
        __configparse_cache()
        print(f"{config_filepath} created with defaults: ENVIORNMENT={ENVIRONMENT}, logger_level={LOGGER_LEVEL}, AWS_REGION={AWS_REGION}")

    #if not pip_credentials_filepath.exists():
    #    __create_pip_update_credentials()

if __name__ == '__main__':
    main()
