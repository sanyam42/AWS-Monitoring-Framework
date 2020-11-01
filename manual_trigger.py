import boto3
import create_sqs

sqs = boto3.resource('sqs')
client = boto3.client('sqs')

# Create Topic and Alarms for all Existing Queues
for queue in sqs.queues.all():  
    create_topicandalarm = create_sqs.create_sqs(queue)
    create_topicandalarm.create_sqs_topics_alarms()
