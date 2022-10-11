import json
import urllib.parse
import boto3



s3 = boto3.client('s3')

sns = boto3.client('sns')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    eventname = event['Records'][0]['eventName']
    sns_message = str("File has been deleted from your Bucket \n\n BUCKET NAME: "+ bucket name +"\n\n FILE NAME: " + key + "\n\n OPERATION: " + eventname + "\n\n")
    try:
        print(eventname)
        if eventname == "DeleteMarkerCreated":
            print("File is Deleted")
            sns_message += str("File Deleted")
 
        print(str(sns_message))
        subject= "S3 Bucket[" + bucket + "] Event[" + eventname + "]"
        print(subject)
        sns_response = sns.publish(
        TargetArn='ARN of SNS topic',
        Message= str(sns_message),
        Subject= str(subject)
        )
    except Exception as err:
        print(err)
        raise err