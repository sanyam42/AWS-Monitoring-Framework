import boto3
import create_sqs

sqs = boto3.resource('sqs')
client = boto3.client('sqs')


def lambda_handler(event, context):
    queue_url = event['responseElements']['queueUrl']
    create_topicandalarm = create_sqs.create_sqs(sqs.Queue(url=queue_url))
    create_topicandalarm.create_sqs_topics_alarms()
