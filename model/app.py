from flask import Flask, Response, request
import pandas as pd
import boto3
import subprocess

sqs = boto3.client('sqs', 'us-east-1')
request_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654147126/1227629236-req-queue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654147126/1227629236-resp-queue'

app = Flask(__name__)

def recieve_request():
    # print("HI")
    while (True):
        response = sqs.receive_message(QueueUrl=request_queue_url,MaxNumberOfMessages=1,WaitTimeSeconds=10,VisibilityTimeout=5,MessageAttributeNames=['All'])
        messages = response.get('Messages', [])
        if messages:
            for message in messages:
                print(message['Body'])
                request_id = message.get('MessageAttributes', {}).get('RequestId', {}).get('StringValue')
                result = subprocess.run(["python3", "face_recognition.py", "../face_images_1000/" + message['Body']], capture_output=True, text = True).stdout.strip("\n")
                # result = result.stdout
                print(result)
                response = sqs.delete_message(QueueUrl=request_queue_url,ReceiptHandle=message['ReceiptHandle'])
                response = sqs.send_message(QueueUrl=response_queue_url,MessageBody=(("{}:{}").format(message['Body'][:-4], result)), MessageAttributes={'RequestId': {'StringValue': request_id, 'DataType': 'String'}})
        else:
            print("No messages found")

if __name__ == "__main__":
    recieve_request()
    app.run(debug=True, host="0.0.0.0", port="4000")