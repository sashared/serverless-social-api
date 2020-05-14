import re
import json
import os

import boto3
import botocore
from boto3.dynamodb.conditions import Key

import api_responses

def get_followed_users_list(event, context):
    dynamodb = boto3.resource('dynamodb')
    user_following_table = dynamodb.Table(os.environ['DYNAMODB_USERFOLLOWING_TABLE'])
    user_table = dynamodb.Table(os.environ['DYNAMODB_USER_TABLE']) 
    user_uuid = event['pathParameters']['user_uuid']
    if not re.match(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', user_uuid):
        return api_responses.get_error_response(404, 'Url parameter is not a valid uuid')

    try:
        user = user_table.get_item(
            Key={
                'user_uuid': user_uuid
            }
        )
        if 'Item' not in user:
            return api_responses.get_error_response(400, 'No user with such id')

        followed_users = user_following_table.query(
            KeyConditionExpression=Key('follower_uuid').eq(user_uuid)
        )
        if 'Items' not in followed_users:
            users_uuids = []
        else:
            users_uuids = [user['followed_uuid'] for user in followed_users['Items']]
        return api_responses.get_success_response(200, json.dumps(users_uuids))

    except botocore.exceptions.ClientError as error:
        error_message = 'An error occured when trying to get followed users list'
        print(error_message)
        print(str(error))
        return api_responses.get_error_response(500, error_message)
