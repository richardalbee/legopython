#pylint: disable=line-too-long, consider-using-dict-items, no-value-for-parameter, consider-iterating-dictionary, logging-fstring-interpolation
'''
Function to interact with restful-booker in Python.
APIS you can test against: https://github.com/toddmotto/public-apis
'''
from legopython import lp_api, lp_settings
from legopython.lp_logging import logger

env_config = {}
for env in ["prod"]:
    env_config[env] = {"api_url": "https://www.reddit.com/"}

#If global envirnment setting is exists as an environment to use, create auth handler.
if lp_settings.ENVIRONMENT in list(env_config.keys()):
    auth_handler = lp_api.AuthHandler(
        name="reddit_basic",
        auth_type=lp_api.AuthType.BASIC,
        env_config=env_config,
        env=lp_settings.ENVIRONMENT
    )
    manage_auth = auth_handler.manage_auth
else:
    logger.warning(f'Example.py will not be able to make calls since {lp_settings.ENVIRONMENT} is not a support environment')


@manage_auth
def ping_reddit_api_page(**kwargs):
    '''Here is an example of how auth and environment is passed through a function.'''
    #Note: This doesn't actually authenticate basic auth.
    return lp_api.send_http_call(
        method='get',
        url=f"{(kwargs.get('api_url'))}",
        headers = {**{'Content-Type': 'application/json'}, **kwargs.get('headers')},
        print_request = True #Used to show the raw request being sent
        )

def main():
    '''Run a test against the weather api'''
    result = ping_reddit_api_page()
    print(result)

if __name__ == '__main__':
    main()
