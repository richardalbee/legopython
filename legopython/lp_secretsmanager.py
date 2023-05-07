#pylint: disable=line-too-long
#This code was taken from "Sample Code" in secrets manager
#Some information used from https://github.com/awslabs/aws-data-wrangler/blob/main/awswrangler/secretsmanager.py
import json
import base64

from typing import Any, Dict, cast, Union
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region_name = 'us-east-1') -> str:
    '''
    Return the raw text of a secret from secrets manager (NOTE -> you probably want to use _v2 and not this)
    secret_name - The name of the secret to retrieve
    region_name (opt) - The region the secret is stored in
    Returns: str
    '''
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name = region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            raise e
        if e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            raise e
        if e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            raise e
        if e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            raise e
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK. # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        return base64.b64decode(get_secret_value_response['SecretBinary'])


def get_secret_v2(secret_name: str, region_name = 'us-east-1') -> Union[Dict,str]:
    '''
    Returns a dictionary of key/values from Secrets Manager
    secret_name - The name of the secret to retrieve
    region_name (opt) - The region the secret is stored in
    Returns: Dict[str, Any] or Str
    '''
    try:
        return cast(Dict[str, Any], json.loads(get_secret(secret_name, region_name)))
    except: #Some secrets are stored only as plain text and not JSON, so return a plain string if that's the case.
        return get_secret(secret_name, region_name)
