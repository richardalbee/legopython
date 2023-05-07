#pylint: disable=line-too-long
'''Module for retrieving, modifying, and deleting data within AWS DynamoDB'''
import time
from datetime import datetime
from getpass import getuser
from functools import wraps
import boto3
from boto3.dynamodb.conditions import Key
from legopython import lp_awssession
from legopython.lp_logging import logger


def delete_prod_dynamodb_indices(partition_key_name:str, partition_key_value:str, sort_key_name:str, sort_key_value:list, dynamo_tablename:str, aws_region='us-east-1'):
    '''Deletes indices from dynamo_tablename given partition keys and sort keys.

    To use, open up table in Dynamo DB and find the following values:

    partition_key_name = name of primary index key of table
    partition_key_value = accepts single value of a given partition key to delete.
    sort_key_name = name of sort key of table
    sort_key_value = accepts list of sort keys to delete in batch
    dynamo_tablename = dynamodb table name
    '''
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    table = dynamodb.Table(dynamo_tablename)
    start_time = time.monotonic()

    batches_of_25 = [sort_key_value[i * 25:(i + 1) * 25] for i in range((len(sort_key_value) + 25 - 1) // 25 )]
    count = 1
    for chunk in batches_of_25:
        items_to_delete = []
        for key in chunk:
            items_to_delete.append({partition_key_name:partition_key_value, sort_key_name:key})

        #TODO: .batch_writer() handles batching on its own. We can rewrite this code to be more efficient: #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/batch_write_item.html
        with table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(Key={
                    partition_key_name: item[partition_key_name], # Change key and value names
                    sort_key_name: item[sort_key_name]
                })
        print(f'batch {count} of {len(batches_of_25)+1} deleted')
        count = count+1
    print(f'Completed deletion of {len(sort_key_value)} {partition_key_name}(s) after {time.monotonic() - start_time} seconds')


def get_dynamodb_sort_key(partition_key_name:str, partition_key_value:str,sort_key_name:str, sort_key_prefix_value:list, dynamo_tablename:str, aws_region='us-east-1') -> list:
    '''Returns sort_key for deleting keys in dynamo_tablename given partion_key and dynamo_tablename.

    partition_key_name = name of primary index key of table
    partition_key_value = accepts single value of a given partition key to delete.
    sort_key_name = name of sort key of table
    sort_key_prefix_value = accepts list of values to search for, returns all values which have the same prefix equal to the provided values.
    dynamo_tablename = dynamodb table name
    '''
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    table = dynamodb.Table(dynamo_tablename)
    start_time = time.monotonic()

    deduped_sort_key_list = list(set(sort_key_prefix_value))
    print(f'Deduped the provided {len(sort_key_prefix_value)} sort_keys down to {len(deduped_sort_key_list)}.')

    count = 1
    results = []
    for sort_key_value in deduped_sort_key_list:
        response = table.query(
            #TODO: design way to multiple searches beyond "begins_with"
            KeyConditionExpression=Key(partition_key_name).eq(partition_key_value) & Key(sort_key_name).begins_with(sort_key_value)
        )
        #if no results are found, do not add to results.
        if response['Items'] != []:
            #TODO: Decide how to handle more than one result:
            for search_result in response['Items']:
                results.append(search_result[sort_key_name])
        if count%100 == 0:
            print(f'Completed for {count} searches of {len(deduped_sort_key_list)} after {time.monotonic() - start_time} seconds.')
        count = count + 1
    print(f'Found {len(results)} {sort_key_name}(s) from {len(sort_key_prefix_value)} provided for {partition_key_value}')
    return results


# arguments that are treated as "captured" by @cloudlog() decorator - used for logging scripts
valid_arguments = {
    "environment",
    "url",
    "config_key",
    "method",
    "value"
}

LOGGING_DYNAMODB_TABLE = "prod-cloudlog"
AWS_REGION = "us-east-1"
ddb = boto3.client("dynamodb",region_name=AWS_REGION)

def cloudlog(arglist=None, username=None):
    '''Decorator function to log execution of a function to DynamoDB'''
    def decorate(func):
        @wraps(func)
        def inner(*args,**kwargs):
            if not lp_awssession.checkSession():
                logger.error("Cannot log without active AWS session.")
                return None
            start = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            then = time.time()
            nonlocal arglist
            if arglist is None:
                arglist = []
            nonlocal username
            if username is None:
                username = getuser()
            try:
                result = func(*args,**kwargs)
                success = True
            except Exception as err:
                success = False
                exception_message = str(err)
                logger.error(str(err))
                result = None
            now = time.time()
            duration_ms = (now-then) * 1000
            captured_args = {}
            uncaptured_args = []
            if len(arglist) > 0 and len(args) > 0:
                kwargs = {**kwargs, **dict(zip(arglist,args))}
            for arg, value in kwargs.items():
                if arg in valid_arguments:
                    captured_args[arg] = {"S": str(value)}
                else:
                    uncaptured_args += [arg]
            dynamo_put_statement = {}
            dynamo_put_statement["username"] = {"S":username}
            dynamo_put_statement["start_time"] = {"S":start}
            dynamo_put_statement["function_name"] = {"S":func.__name__}
            dynamo_put_statement["duration_ms"] = {"N":f"{duration_ms:0.4f}"}
            dynamo_put_statement["captured_args"] = {"M":captured_args}
            dynamo_put_statement["success"] = {"BOOL":success}
            if len(uncaptured_args) > 0:
                dynamo_put_statement["uncaptured_args"] = {"SS":uncaptured_args}
            if not success:
                dynamo_put_statement["exception_message"] = {"S":exception_message} #pylint: disable=used-before-assignment
            ddb.put_item(
                TableName = LOGGING_DYNAMODB_TABLE,
                Item = dynamo_put_statement
            )
            return result
        return inner
    return decorate

