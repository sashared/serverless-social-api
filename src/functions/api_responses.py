import json

def get_error_response(status_code, error_message):
    return {
        'statusCode': status_code,
        'body': json.dumps({ 'message': error_message })
    } 

def get_success_response(status_code = 200, body = None):
    return {
        'statusCode': status_code,
        'body': body
    }