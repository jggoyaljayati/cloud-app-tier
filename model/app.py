import pandas as pd
import boto3
import face_recognition

s3 = boto3.client('s3', region_name='us-east-1')
sqs = boto3.client('sqs', 'us-east-1')
request_queue_url = 'https://sqs.us-east-1.amazonaws.com/975049916042/1227629236-req-queue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/975049916042/1227629236-resp-queue'
output_bucket = '1227629236-out-bucket'

def recieve_request():
    while (True):
        try:
            response = sqs.receive_message(QueueUrl=request_queue_url,MaxNumberOfMessages=1,WaitTimeSeconds=4,MessageAttributeNames=['All'])
            messages = response.get('Messages', [])
            if messages:
                for message in messages:
                    print(message['Body'])
                    request_id = message.get('MessageAttributes', {}).get('RequestId', {}).get('StringValue')
                    result = face_recognition.face_match("../face_images_1000/" + message['Body'], 'data.pt')[0]
                    print(result)
                    output_key = message['Body'][:-4]
                    output_value = result
                    s3.put_object(Bucket=output_bucket, Key=output_key, Body=output_value)
                    response = sqs.send_message(QueueUrl=response_queue_url,MessageBody=(("{}:{}").format(message['Body'][:-4], result)), MessageAttributes={'RequestId': {'StringValue': request_id, 'DataType': 'String'}})
                    response = sqs.delete_message(QueueUrl=request_queue_url,ReceiptHandle=message['ReceiptHandle'])
            else:
                print("No messages found")
        except Exception as e:
            print("Error: ", e)


if __name__ == "__main__":
    print("Started")
    recieve_request()