#pylint: disable=line-too-long
'''
Handles API calls for other MoxePython scripts.
'''

from enum import Enum
from functools import wraps
from getpass import getpass
from pathlib import Path
from time import time
import json
import base64
import sys
from json.decoder import JSONDecodeError
import requests
from legopython.lp_logging import logger

class InvalidStatusReturned(Exception):
    '''No action when an invalid HTTP status is returned.'''
    pass


def print_raw_request(requesttype:str, input_url: str, input_headers:dict = None, input_payload:dict = None, input_params:dict = None):
    """pretty prints raw http requests to console for troubleshooting purposes."""

    req = requests.Request(requesttype, url = input_url, headers = input_headers, data = input_payload, params = input_params)
    req = req.prepare()

    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))
    print('\nPrinted API call above for troubleshooting, exiting.')
    sys.exit()


def get_api_json(url, valid_statuses=None, pretty_print:bool=False, **kwargs):
    '''
    A handler for the get requests module to return JSON and handle any unexpected statuses.
    Optional: pretty_print = True to print json. Useful for troubleshooting.
    '''
    response = requests.get(url, **kwargs)

    if response.status_code in (valid_statuses or [200, 201]):
        return response.json()
    input_headers = kwargs.pop('headers')
    if pretty_print:
        print_raw_request('GET', url, input_headers)
    raise InvalidStatusReturned("Response from {} returned status code {}: {} \n{}".format(response.url, response.status_code, response.reason, response.content))


def post_api_json(url, valid_statuses=None,pretty_print:bool=False, **kwargs):
    '''
    A handler for the posts requests module to return JSON and handle any unexpected statuses.
    Optional: pretty_print = True to print json. Useful for troubleshooting.
    '''
    response = requests.post(url, **kwargs)
    if response.status_code in (valid_statuses or [200, 201, 204]):
        if response.status_code != 204: #No content returned, breaks response.json()
            try:
                logger.debug(f"Success, HTTP {response.status_code}.")
                return response.json()
            except JSONDecodeError:  # includes simplejson.decoder.JSONDecodeError
                logger.debug(f"Success, HTTP {response.status_code}. No Content Returned.")
                return {}
        else:
            logger.info("Success, HTTP 204 No Content returned.")
            return {}
    else:
        input_headers = kwargs.pop('headers')
        input_payload = kwargs.pop('data')
        if pretty_print:
            print_raw_request('POST', url, input_headers, input_payload)
        raise InvalidStatusReturned("Response from {} returned status code {}: {} \n{}".format(response.url, response.status_code, response.reason, response.content))


def put_api_json(url, valid_statuses=None, pretty_print:bool=False, **kwargs):
    '''
    A handler for the put requests module to return JSON and handle any unexpected statuses.
    Optional: pretty_print = True to print json. Useful for troubleshooting.
    '''
    response = requests.put(url,**kwargs)
    if response.status_code in (valid_statuses or [200, 204]):
        if response.status_code != 204: #No content returned, breaks response.json()
            return response.json()
        else:
            #Changed to logger.info for succinct multithreaded printouts.
            logger.info(f"Success, HTTP 204 No Content returned.")
            return {}
    else:
        input_headers = kwargs.pop('headers')
        input_payload = kwargs.pop('data')
        if pretty_print: print_raw_request('PUT', url, input_headers, input_payload)
        raise InvalidStatusReturned("Response from {} returned status code {}: {} \n{}".format(response.url, response.status_code, response.reason, response.content))


def delete_api_json(url, valid_statuses=None,pretty_print:bool=False, **kwargs):
    '''
    A handler for the requests module to return JSON and handle any
    unexpected statuses. This one is for posts.
    Optional: pretty_print = True to print json. Useful for troubleshooting.
    '''
    response = requests.delete(url,**kwargs)
    if response.status_code not in (valid_statuses or [204]):
        input_headers = kwargs.pop('headers')
        if pretty_print: print_raw_request('DELETE', url, input_headers)
        raise InvalidStatusReturned("Response from {} returned status code {}: {} \n{}".format(response.url, response.status_code, response.reason, response.content))


class AuthType(Enum):
    """Different authentication types supported by the AuthHandler."""
    BASIC = 1
    JWT_BEARER = 2

moxe_folder = Path.home() / ".pythontoolscreds"

class AuthHandler:
    """Handles authentication for APIs."""
    def __init__(self, name:str, auth_type:AuthType, env_config:list, env:str = 'prod') :
        self.name = name
        self.auth_type = auth_type
        self.env_config = env_config
        self.env = env
        self.credentials = None

    @property
    def name(self):
        """Name for the function using the auth handler"""
        return self._name

    @name.setter
    def name(self, name:str):
        self._name = name

    @property
    def auth_type(self):
        """Auth type for the API"""
        return self._auth_type

    @auth_type.setter
    def auth_type(self, auth_type:AuthType):
        self._auth_type = auth_type

    @property
    def env_config(self):
        """The config for each environment"""
        return self._env_config

    @env_config.setter
    def env_config(self,env_config):
        self._env_config = env_config

    @property
    def env(self):
        """Which environment in the env_config to use"""
        return self._env

    @env.setter
    def env(self, env):
        if env not in self.env_config.keys():
            #raise TypeError(f"Environment {env} not in environment config")
            #In some cases you want to run QA env but QA env does not exist for Camudna. So, this should not error but instead not be a hard stop.
            #How do we get this to warn that Camunda doesn't have QA, for example?
            logger.warn(f"Environment {env} does not exist as a config")
        else:
            self._env = env
        #if the environment changes we want to eliminate the cached credentials
        self.credentials = None

    @property
    def credentials(self):
        """The active credentials used to authenticate"""
        return self._credentials

    @credentials.setter
    def credentials(self, credentials):
        self._credentials = credentials

    def _get_cached_credentials(self):
        """Private function to get credentials stored on disk"""
        Path(moxe_folder).mkdir(exist_ok=True)
        cached_credential_path = Path(moxe_folder) / f"{self.name}-{self.env}.json"
        credfile = Path(cached_credential_path)
        if not credfile.exists():
            logger.debug("Could not find cached credentials at %s", cached_credential_path)
            return None
        return json.loads(credfile.read_text(encoding='utf-8'))

    def _cache_credentials(self):
        """Private function to store credentials on disk"""
        Path(moxe_folder).mkdir(exist_ok=True)
        cached_credential_path = Path(moxe_folder) / f"{self.name}-{self.env}.json"
        credfile = Path(cached_credential_path)
        credfile.write_text(json.dumps(self.credentials),encoding="utf-8")

    def clear_cached_credentials(self):
        """Clears credentials cached on disk and in memory"""
        Path(moxe_folder).mkdir(exist_ok=True)
        cached_credential_path = Path(moxe_folder) / f"{self.name}-{self.env}.json"
        cached_credential_path.unlink()
        self.credentials = None

    def _get_basic_auth_credentials(self):
        """Prompt for basic authentication credentials and return the username and auth string"""
        username = input(f"Enter the username for {self.name} {self.env}: ")
        password = getpass(f"Enter the password for {self.name} {self.env}: ")
        return username, base64.b64encode(bytes(f"{username}:{password}",encoding='utf8')).decode('utf-8')

    def _request_token(self):
        """
        Calls a token URL to request a new Java Web Token.
        """
        token_params = self.env_config.get(self.env).get("token_params")
        for base_key,base_value in token_params.items():
            if isinstance(base_value,dict):
                for key,value in base_value.items():
                    if callable(value):
                        logger.debug("Config item %s for %s is a function, calling function to update value",key,base_key)
                        token_params[base_key][key] = value()
        return post_api_json(**token_params)

    def get_valid_credentials(self):
        """
        Function that ensures the present authentication values are valid
        and not expired, and if they don't exists it gets some.
        """
        now = int(time())
        if self.credentials is None:
            logger.debug("Trying to get cached credentials")
            self.credentials = self._get_cached_credentials()
        if self.credentials is None or (self.credentials.get('expiry') and self.credentials.get('expiry',0) <= now):
            logger.debug('Getting new authentication credentials')
            self.credentials = {}
            self.credentials['received'] = now
            if self.auth_type == AuthType.BASIC:
                self.credentials["username"],self._credentials["credstring"] = self._get_basic_auth_credentials()
                self.credentials["auth_header"] = f"Basic {self._credentials.get('credstring')}"
            elif self.auth_type == AuthType.JWT_BEARER:
                self.credentials = self._request_token()
                self.credentials['expiry'] = now + self._credentials.get('expires_in',3600)
                self.credentials['auth_header'] = f"Bearer {self._credentials.get('access_token')}"
        self._cache_credentials()
        return self.credentials

    def manage_auth(self, func):
        """Decorator to handle authentication"""
        @wraps(func)
        def inner(*args,**kwargs):
            creds = self.get_valid_credentials()
            kwargs["api_url"] = kwargs.setdefault("api_url",self.env_config.get(self.env).get("api_url"))
            kwargs["headers"] = kwargs.setdefault("headers",{})
            kwargs["headers"]["Authorization"] = creds.get("auth_header")
            return func(*args,**kwargs)
        return inner
