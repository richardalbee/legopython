#pylint: disable=line-too-long, invalid-name
'''
AWS Secret Manager api functions via Boto 3: https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_ListSecrets.html
'''
import base64
import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name: str, region_name = 'us-east-2') -> dict:
    '''
    Return the a decrypted, current version, secret from secrets manager as dict
    secret_name - The name of the secret to retrieve  or the the Amazon Resource Name (ARN)
    region_name (opt) - The region the secret is stored in
    Returns: Returns {'secret': secret} if rawtext or dict of key-value entries
    '''
    # Create a Secrets Manager client session #TODO: Find more efficient way to load session without duplicating code?
    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name = region_name
    )

    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager/client/get_secret_value.html#
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e: #Exception list: https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    else:
        # Returns secret whether its a string or binary, 'SecretString' or 'SecretBinary' is populated
        if 'SecretString' in get_secret_value_response:
            if isinstance(get_secret_value_response['SecretString'], dict):
                return get_secret_value_response['SecretString']
            elif isinstance(get_secret_value_response['SecretString'], str): #Some secrets are stored only as plain text and not JSON, so return a dict with a key of 'secret'
                return {'secret': get_secret_value_response['SecretString']} #secret
            else:
                raise ValueError('Unable to parse SecretString, did not recieve str or dict')
            
        elif 'SecretBinary' in get_secret_value_response:
            return {'secret':base64.b64decode(get_secret_value_response['SecretBinary'])}
        else:
            raise ValueError('A SecretString or SecretBinary was not recieved from from request.')


def create_secret(secret_name:str, secret_value:str, description:str = '', search_tags:list = None, force_overwrite:bool = False, region_name:str = 'us-east-2') -> dict:
    '''
    Creates a secretManager secretString, does not support SecretBinary
    #TODO Allow SecretBinary support, can also support versioning, and replication

    secret_name = accepts alphanumeric string and /_+=.@-
    secret_value = accepts plain string or string formatted json, max len 65536: '{"key1":"value1, "key2":"value2"}'
    description = Readable text explaining the use of the secret
    search_tags = searchable tags, Each tag is a key and value pair of strings in a JSON text string: [{"Key":"CostCenter","Value":"12345"},{"Key":"environment","Value":"production"}]
    force_overwrite = Boolean, if true will overwrite an identically named secret
    region_name = Specifies aws instance to create the secret

    Returns a http Json response of the result

    Reference Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager/client/create_secret.html
    '''
    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name = region_name
    )

    if search_tags:
        return client.create_secret(Name = secret_name, Description = description, SecretString = secret_value, Tags=search_tags,ForceOverwriteReplicaSecret = force_overwrite)
    else:
        return client.create_secret(Name = secret_name, Description = description, SecretString = secret_value, ForceOverwriteReplicaSecret = force_overwrite)
