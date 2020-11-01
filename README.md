# Project Details
Basically this project is the monitoring framework which can be used to monitor the SQS queues. This code can be used to apply monitoring to the existing queues as well as new queues. Used python SDK boto3 to create, configure and manage the AWS resources. We need to configure the AWS Access Key ID, Secret Access Key and region name in aws config.

## Monitor existing SQS queues
For monitoring existing queues, we can execute the python file manual_trigger.py . This will fetch the list of all existing SQS queues from the AWS account and will create SNS topics, subscriptions and add alarms for all queues one by one.

## Add monitoring to new SQS queues
For adding monitoring to the new queues as soon as they are created, we need to follow the below steps.
1) Enable the CloudTrail logs from the AWS console.
2) Go to Cloudwatch -> Events -> Rules -> Create rule
3) Select 'Event Pattern' in the Event Source as we need to trigger the lambda function when new queue is created.
4) Select Service Name as 'Simple Queue Service (SQS)' and Event Type as 'AWS API Call via CloudTrail'.
5) Select operation as 'Specific Operation(s)' and enter operation value as CreateQueue in the textbox.
6) Add target as the lambda function and select the lambda function which we are creating below.


## Add Lambda functions
1) Open lambda console and select "Create function". Enter the function name and select rumtime as Python 3.x
2) Deploy the following scripts to the lambda function
   - lambda_function.py
   - create_sqs.py
   - create_topic_and_subscription.py
   - create_alarms.py

On event of creating new queue, this lambda function will be triggered. Event will pass only newly created Queue Name as input to the lambda function. So SNS topics, subscriptions and alarms etc. will be created for new queue only.


## Creating new Queues
New SQS queues are created by the developers. Whenever they will create the queue, they need to add the following tags to the queue. 
- Owner: 'Team Name'                               # SNS topic will be created with the team name
- Email: 'gumbersanyam@gmail.com alex@gmail.com'   # Space separated emails which will get the alerts from cloudwatch.
- SentMessageSize: '250000'                        # This will override the default threshold
- SentMessageSize: '80 percent'                    # This will set the threshold as 80% of MaximumMessageSize

You can add custom thresholds for other metrics as well which are defined in the create_sqs.py script. 


## create_sqs.py
- Both manual trigger and Event trigger are invoking this python script. 
- This script is having metrics list which need to be monitored for SQS queues. If any metric need to be added/removed, list need to be  updated here.
- Default thresholds for all metrics are also defined in this script in python dictionay object thresholds. This dictionay object also   contains operator and units of monitoring.
  "NumberOfMessagesSent" : {"unit": "Count", "threshold": "10", "operator": "LessThanThreshold"}
- For some metrics like SentMessageSize, we can't have fixed threshold value as they can vary from queue to queue. So for this we have   added the percentage threshold for the Source like MaximumMessageSize. So threshold for metric SentMessageSize will be 75% of MaximumMessageSize
  "SentMessageSize": {"unit": "Bytes", "threshold": "75 percent", "operator": "GreaterThanThreshold", "source": "MaximumMessageSize"}

- Default owner and subscription is defined to the central team. If Owner and Email tag is not defined for the queue, it will send alerts to the default subscriptions i.e central team.
- Similary if tags are defined for the queue as  metrics name like SentMessageSize, then it will pick the threshold value from tags else threshold will be picked from default.


## create_topic_and_subscription.py
- create_sqs script calls this script for creating topic and subscriptions. Script passes Owner and Email tags to this.
- Topic will be created with the Owner Name.
- Subscriptions list will be fetched for the above topic. If email id is not subscribed for this topic, then it will create the subscription and email will be sent. If email is subscribed but in PendingConfirmation state, it will notify the user to subscribe. If emailid is subscribed, then this script will do nothing.


## create_alarms.py
- For each metric defined in the create_sqs script, this script will be called and metric, threshold, operator, unit, queue name etc arguments are passed to this script.
- This will create the cloudwatch alarm for the metric, set the threshold value and send alerts to the emails defined in tags.
- If alarm already exists for the queue for particular metric, it will update the alarm if there is some update in threshold values, topic name. If there is no update in the values, there will be no change in the alarm.


## Metrics to Monitor for Queues
I have picked below metrics which should be monitored for SQS queues.

1) ApproximateAgeOfOldestMessage = Should give alert when message is still in the queue and close to the MessageRetentionPeriod defined for the queue.
2) SentMessageSize =  Alert should be raised when message size is close to the MaximumMessageSize.
3) ApproximateNumberOfMessagesDelayed = If there are high number of messages getting delayed.
4) ApproximateNumberOfMessagesVisible =  If there are high number of messages available for retrieval from the queue.
5) NumberOfMessagesSent =  If there is fall in the number of messages sent to the Queue. Need to check if producers are working fine.
6) NumberOfMessagesReceived = If there is fall in the number of messages received from the Queue. Need to check if consumers are working fine.


## Extensible
We can extend the code to monitor other AWS service like EC2 etc. We can use the same scripts create_topic_and_subscription.py and create_alarms.py. We will have to create a new script which will have metrics list for EC2 and default thresholds, similar to the create_sqs.py. Also we will have to update the lambda_function.py which will create alarm as new EC2 instance is created. Also we can update the manual_trigger.py which can fetch the all existing ec2 instances list and can create alarms.
