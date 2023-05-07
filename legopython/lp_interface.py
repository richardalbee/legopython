#pylint: disable=line-too-long, consider-using-dict-items, no-value-for-parameter, consider-iterating-dictionary, logging-fstring-interpolation
''' A tool for calling legopython functions.

To add a function to legopython UI, add an entry to support_functions_menu and a if user_input == x: statement.
Any function added must have type hinting on every parameter or have those parameters missing type hinting skipped.
'''
import ast
import time
import types
import typing
import subprocess
import sys
from legopython import lp_general, lp_settings
from legopython.lp_logging import logger


def list_function_parameters(function: str) -> dict:
    '''Get a list of parameters and typing hints from an explicit moxePython function.'''
    function_annotations = function.__annotations__
    if 'return' in function_annotations.keys():
        function_annotations.pop('return', None)
    return function_annotations


def prompt_user(question: str) -> str:
    '''Prompt a user and return a string. Allow exiting if they type it.'''
    user_input = input(question)
    if user_input.lower() in ('exit','quit',"'quit'","'exit'",'"exit"','"quit"'):
        print('f\n {user_input} detected, Exiting')
        sys.exit()
    return user_input

def prompt_set_environment():
    '''Prompt user to set the MoxePython global environment'''
    environment_dict = {
        1: {'name':'prod'},
        2: {'name':'qa'},
        3: {'name':'test'},
        4: {'name':'int'}
    }
    print('0. Return\n')
    for key,value in environment_dict.items():
        print(f'{key}: {value["name"]}')
    user_response = lp_general.prompt_user_int('Enter # for ENV you want to change to', maximum=len(environment_dict))

    if user_response == 0:
        logger.info(f'Exiting without changing Env. Env currently set to {lp_settings.ENVIRONMENT}')
        return support_functions_menu()
    lp_settings.set_environment(environment_dict[user_response]['name'])

def prompt_user_string(parameter_name:str):
    '''Prompts user to enter string input, returns string'''
    user_input = prompt_user(f"Enter input for {parameter_name}: ")
    if user_input == '':
        return user_input
    if user_input.startswith("'") and user_input.endswith("'"): #Remove ''
        user_input = user_input.replace("'","")
    if user_input.startswith('"') and user_input.endswith('"'): #Remove ""
        user_input = user_input.replace('"',"")
    return user_input

def prompt_user_bool(parameter_name:str):
    '''Prompts user to enter bool input, returns bool'''
    valid_input = False
    while valid_input is False:
        user_input = prompt_user(f"Enter true/false or y/n for {parameter_name}: ")
        if user_input == '':
            valid_input = True
        if user_input.startswith("'") and user_input.endswith("'"): #Remove ''
            user_input = user_input.replace("'","")
        if user_input.startswith('"') and user_input.endswith('"'): #Remove ""
            user_input = user_input.replace('"',"")
        if user_input.lower() in ('y', 'true'):
            user_input = True
            valid_input = True
        elif user_input.lower() in ('n', 'false'):
            user_input = False
            valid_input = True
        elif valid_input is not True:
                print(f'Please enter true/false or y/n for {parameter_name}')
    return user_input

def prompt_user_int(parameter_name:str):
    '''Prompts user to enter int, returns int'''
    valid_input = False
    while valid_input is False:
        user_input = prompt_user(f'Enter whole number for {parameter_name}: ')
        if user_input == '':
            valid_input = True
        if user_input.isdigit():
            user_input = int(user_input)
            valid_input = True
        elif valid_input is not True:
            print(f'Please enter value for {parameter_name} in "7" or "100" format')
    return user_input

def prompt_user_list(parameter_name:str):
    '''Prompts user to enter list input, returns list'''
    valid_input = False
    while valid_input is False:
        user_input = prompt_user(f"Enter input for {parameter_name} as ['str','str'] or filename of a headerless 1 column CSV as 'excelfilename.csv': ")
        if user_input == '':
            valid_input = True
        if user_input.startswith('[') and user_input.endswith(']'):
            user_input = ast.literal_eval(user_input)
            valid_input = True
        elif user_input.endswith('.csv'):
            user_input = lp_general.read_csv(user_input, hasheader = False)
            valid_input = True

        if valid_input is not True:
            print(f"Please enter value for {parameter_name} as list ['str','str'] or excelfilename.csv")

    return user_input

def prompt_user_dict(parameter_name:str):
    '''Prompts user to enter dict input, returns dict'''
    valid_input = False
    while valid_input is False:
        user_input = prompt_user(f'f"Enter input for parameter for {parameter_name} in dict format {"key": "value", "key": "value"}')
        if user_input == '':
            valid_input = True
        if user_input.startswith('{') and user_input.endswith('}'):
            user_input = ast.literal_eval(user_input)
            valid_input = True
        elif valid_input is not True:
            print(f'Please enter value for {parameter_name} in dict format {"key": "value", "key": "value"}')
    return user_input

def prompt_user_parameters(function_name, skip_params:list, prompt=True) -> dict:
    '''Prompt user for each parameter of {function_name}, do not format as a string
    Allows skipping params in list of ints format. [int,int,int]
    '''
    parameter_dict = list_function_parameters(function_name)

    all_params_skipped = True
    for count, parameter in enumerate(parameter_dict):
        if count not in skip_params:
            all_params_skipped = False
    if all_params_skipped: #skip asking for params if all parameters are skipped
        return {}

    print('\n')
    help(function_name)
    parameter_input = {}
    print('(blank=skip // quit/exit returns to menu.)\n')
    for count, parameter in enumerate(parameter_dict):
        if count not in skip_params:

            if parameter_dict[parameter] == type('string'): #prompt for a string
                user_input = prompt_user_string(parameter)
            if parameter_dict[parameter] == type(False): #prompt for bool
                user_input = prompt_user_bool(parameter_name=parameter)
            if parameter_dict[parameter] == type(7): #prompt for int
                user_input = prompt_user_int(parameter_name=parameter)
            if parameter_dict[parameter] == type(['str','str','str']): #prompt for list
                user_input = prompt_user_list(parameter_name=parameter)
            if parameter_dict[parameter] == type({"key": "value"}): #prompt for dict, avoid this data input for legopython functions.
                user_input = prompt_user_list(parameter_name=parameter)
            if parameter_dict[parameter] == typing.Union[list, str]: #moxeRequests.Unpark requests has a type hint which doesn't work well here.
                user_input = prompt_user_list(parameter_name=parameter)

            try: #If user entered blank, skip. Else, add to kwargs dictionary.
                if user_input != '':
                    parameter_input[parameter] = user_input
            except UnboundLocalError:
                print(f'{parameter_dict[parameter]} is not a supported type; bug with {function_name}. Exiting.')
                time.sleep(3)
                return support_functions_menu()

    if prompt:
        print(f'\n {parameter_input} \n')
        if not lp_general.yesno(question=f"Are you sure you want to run {function_name.__name__} with the parameters above?"):
            return support_functions_menu()
    return parameter_input

def support_functions_menu():
    ''' Prints available functions and allows selection of function in support_functions_dict'''

    support_functions_dict = {
        0   : {'name':f'CURRENT ENV = {lp_settings.ENVIRONMENT}','function':prompt_set_environment,'skip_param':[1]},
        1   : {'name':'Update legopython: pip install','function':'pip install --upgrade legopython -i https://app.jfrog.io/artifactory/api/pypi/moxe-pypi/simple','skip_param':[]} 
    }

    #Display menu
    for key,value in support_functions_dict.items():
        if key == 0:
            print(f'\n{key}: {value["name"]}\n')
        else:
            print(f'{key}: {value["name"]}')
    print('\nCtrl + C or type exit to close.')

    user_input = lp_general.prompt_user_int('\nEnter the number for a Support Function ', maximum=(len(support_functions_dict)-1))

    if isinstance(support_functions_dict[user_input]['function'], types.FunctionType): #If the support dict function is a function instead of a string:
        func = support_functions_dict[user_input]['function']
        skip_params = support_functions_dict[user_input]['skip_param']
        user_parameters = prompt_user_parameters(func, skip_params)
        if user_parameters == {}: #if no user parameters entered or if all parameters skip, do not submit parameters
            func()
        else:
            func(**user_parameters)

        print(f"\nCompleted running function {support_functions_dict[user_input]['function'].__name__}. Returning to main menu.")
    else:
        subprocess.call(support_functions_dict[user_input]['function'],shell=True)
        print(f"\nCompleted running function {support_functions_dict[user_input]['function']}. Returning to main menu.")

    time.sleep(3)
    return support_functions_menu()


def main():
    ''' Start the interface loop for legopython text UI'''
    support_functions_menu()


if __name__ == '__main__':
    main()
