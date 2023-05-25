'''Module for retrieving and deleting data within AWS DynamoDB'''
import time
import boto3
from boto3.dynamodb.conditions import Key


def sortkey_prefix_search(partition_key_name:str, partition_key_value:str, sort_key_name:str, sort_key_prefix_value:list, dynamo_tablename:str, aws_region='us-east-2') -> list:
    '''Returns sort_key for deleting keys in dynamo_tablename given partion_key and dynamo_tablename.

    partition_key_name = name of primary index key of table
    partition_key_value = accepts single value of a given partition key to search.
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
            KeyConditionExpression=Key(partition_key_name).eq(partition_key_value) & Key(sort_key_name).begins_with(sort_key_value)
        )
        #if no results are found, do not add to results.
        if response['Items'] != []:
            for search_result in response['Items']:
                results.append(search_result[sort_key_name])
        if count%100 == 0:
            print(f'Completed for {count} searches of {len(deduped_sort_key_list)} after {time.monotonic() - start_time} seconds.')
        count = count + 1
    print(f'Found {len(results)} {sort_key_name}(s) from {len(sort_key_prefix_value)} provided for {partition_key_value}')
    return results


def delete_indices(partition_key_name:str, partition_key_value:str, sort_key_name:str, sort_key_value:list, table_name:str, batch_size:int = 50, aws_region='us-east-2') -> None:
    '''Deletes indices from dynamo_tablename given partition keys and sort keys.

    To use, open up table in Dynamo DB and find the following values:

    partition_key_name = name of primary index key of table
    partition_key_value = accepts single value of a given partition key to delete.
    sort_key_name = name of sort key of table
    sort_key_value = accepts list of sort keys to delete in batch
    dynamo_tablename = dynamodb table name
    '''
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    dynamodb_table = dynamodb.Table(table_name)
    start_time = time.monotonic()

    batches = [sort_key_value[i * batch_size:(i + 1) * batch_size] for i in range((len(sort_key_value) + batch_size - 1) // batch_size )]
    count = 1
    for chunk in batches:
        items_to_delete = []
        for key in chunk:
            items_to_delete.append({partition_key_name:partition_key_value, sort_key_name:key})

        #TODO: .batch_writer() handles batching on its own. We can rewrite this code to be more efficient: #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/batch_write_item.html
        with dynamodb_table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(Key={
                    partition_key_name: item[partition_key_name], # Change key and value names
                    sort_key_name: item[sort_key_name]
                })
        print(f'Batch {count} of {len(batches)+1} deleted.')
        count = count+1
    print(f'Completed deletion of {len(sort_key_value)} {partition_key_name}(s) after {time.monotonic() - start_time} seconds')
