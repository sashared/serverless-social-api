import json
import os

import boto3
import botocore

import api_responses


USER_TABLE_NAME = os.environ['DYNAMODB_USER_TABLE']
USER_FOLLOWING_TABLE_NAME = os.environ['DYNAMODB_USERFOLLOWING_TABLE']
ERROR_MESSAGE = 'An error occured when trying to follow user'
NO_USER_WITH_CURRENT_USER_ID_ERROR_MESSAGE = 'No user with given current user id'
NO_USER_WITH_ANOTHER_USER_ID_ERROR_MESSAGE = 'No user with given another user id'
CANNOT_FOLLOW_YOURSELF_ERROR_MESSAGE = 'Cannot follow yourself!'
ALREADY_FOLLOWING_ERROR_MESSAGE = 'Already following!'


def follow_user(event, context):
    dynamodb = boto3.resource('dynamodb')
    user_following_table = dynamodb.Table(USER_FOLLOWING_TABLE_NAME)
    user_table = dynamodb.Table(USER_TABLE_NAME)
    data = json.loads(event['body'])
    current_user_uuid = data['current_user_uuid']
    another_user_uuid = data['another_user_uuid']

    try:
        current_user = user_table.get_item(
            Key={
                'user_uuid': current_user_uuid
            }
        )
        if 'Item' not in current_user:
            return api_responses.get_error_response(400, NO_USER_WITH_CURRENT_USER_ID_ERROR_MESSAGE)
        
        another_user = user_table.get_item(
            Key={
                'user_uuid': another_user_uuid
            }
        )
        if 'Item' not in another_user:
            return api_responses.get_error_response(400, NO_USER_WITH_ANOTHER_USER_ID_ERROR_MESSAGE)

        if current_user_uuid == another_user_uuid:
            return api_responses.get_error_response(400, CANNOT_FOLLOW_YOURSELF_ERROR_MESSAGE)

        user = user_following_table.get_item(
            Key={
                'follower_uuid': current_user_uuid,
                'followed_uuid': another_user_uuid
            }
        )
        if 'Item' in user:
            return api_responses.get_error_response(400, ALREADY_FOLLOWING_ERROR_MESSAGE)
            

        user_following_table.put_item(
            Item={
                'follower_uuid': current_user_uuid,
                'followed_uuid': another_user_uuid
            }
        )        
        return api_responses.get_success_response(204)
    except botocore.exceptions.ClientError as error:
        print(ERROR_MESSAGE)
        print(str(error))
        return api_responses.get_error_response(500, ERROR_MESSAGE)
