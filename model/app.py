# from flask import Flask, Response, request
# import os
import pandas as pd
import boto3
# import subprocess
import face_recognition

s3 = boto3.client('s3', region_name='us-east-1')
sqs = boto3.client('sqs', 'us-east-1')
request_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654147126/1227629236-req-queue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654147126/1227629236-resp-queue'
output_bucket = '1227629236-out-bucket'
# app = Flask(__name__)

def recieve_request():
    # print("HI")
    while (True):
        response = sqs.receive_message(QueueUrl=request_queue_url,MaxNumberOfMessages=1,WaitTimeSeconds=4,MessageAttributeNames=['All'])
        messages = response.get('Messages', [])
        if messages:
            # print(messages)
            for message in messages:
                print(message['Body'])
                request_id = message.get('MessageAttributes', {}).get('RequestId', {}).get('StringValue')
                # result = subprocess.run(["python3", "face_recognition.py", "../face_images_1000/" + message['Body']], capture_output=True, text = True).stdout.strip("\n")
                # result = result.stdout
                # image_path = "../face_images_1000/" + message['Body']
                # command = f'python3 "face_recognition.py" "{image_path}"'
                # result = os.popen(command).read()
                # print(result)
                result = face_recognition.face_match("../face_images_1000/" + message['Body'], 'data.pt')[0]
                print(result)
                output_key = message['Body'][:-4]
                output_value = result
                s3.put_object(Bucket=output_bucket, Key=output_key, Body=output_value)
                response = sqs.send_message(QueueUrl=response_queue_url,MessageBody=(("{}:{}").format(message['Body'][:-4], result)), MessageAttributes={'RequestId': {'StringValue': request_id, 'DataType': 'String'}})
                response = sqs.delete_message(QueueUrl=request_queue_url,ReceiptHandle=message['ReceiptHandle'])
        else:
            print("No messages found")

if __name__ == "__main__":
    print("Started")
    recieve_request()
    # app.run(debug=True, host="0.0.0.0", port="4000")