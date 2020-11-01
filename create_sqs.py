import create_topic_and_subscription
import create_alarms
import boto3

sqs = boto3.resource('sqs')
client = boto3.client('sqs')

# METRICS which need to be set on Cloudwatch
metrics = [ 'ApproximateAgeOfOldestMessage', 'ApproximateNumberOfMessagesDelayed', 'ApproximateNumberOfMessagesVisible', 'NumberOfMessagesSent', 'NumberOfMessagesReceived', 'SentMessageSize' ]


# Default Thresholds for Metrics
thresholds = {
    "ApproximateAgeOfOldestMessage" : {"unit": "Seconds", "threshold": "75 percent", "operator": "GreaterThanThreshold", "source": "MessageRetentionPeriod"},
    "ApproximateNumberOfMessagesDelayed" : {"unit": "Count", "threshold": "100", "operator": "GreaterThanThreshold"},
    "ApproximateNumberOfMessagesVisible" : {"unit": "Count", "threshold": "100", "operator": "GreaterThanThreshold"},
    "NumberOfMessagesSent" : {"unit": "Count", "threshold": "10", "operator": "LessThanThreshold"},
    "NumberOfMessagesReceived" : {"unit": "Count", "threshold": "10", "operator": "LessThanThreshold"},
    "SentMessageSize": {"unit": "Bytes", "threshold": "75 percent", "operator": "GreaterThanThreshold", "source": "MaximumMessageSize"}
}


# Default Owner
default_owner = "CentralTeam"

#Default Subscription
default_subscription = "centralteam@paytm.com"

# Class will create SQS topics, subscriptions and alarms for all existing queues 
class create_sqs:
    def __init__(self, queue):
                  self.queue = queue

    def create_sqs_topics_alarms(self):
    
        print("\n#################################################################\n")
        print("Queue URL is " + self.queue.url)

        queue_name = self.queue.url.split('/')[4]
        print("Queue name is " + queue_name)

        # Check if Tags exists, else
        if u'Tags' in client.list_queue_tags(QueueUrl=self.queue.url):
            tags_list = client.list_queue_tags(QueueUrl=self.queue.url)[u'Tags']
        else:
            print("Tags doesn't exists, skipping or exit")
            tags_list = {}

        if 'Owner' in tags_list:
            topic_name = client.list_queue_tags(QueueUrl=self.queue.url)[u'Tags']['Owner']
            print("Value for tag Owner is " + topic_name)
        else:
            print("Tag Owner doesn't exists, picking up default Owner")
            topic_name = default_owner


        if 'Email' in tags_list:
            subscriptions = client.list_queue_tags(QueueUrl=self.queue.url)[u'Tags']['Email']
            print("Value for tag Email is " + subscriptions)
        else:
            print("Tag Email doesn't exists, picking up default subscriptions")
            subscriptions =  default_subscription

        
        # Create Topic and Subscriptions
        create_TnS = create_topic_and_subscription.create_topic_and_subscription(topic_name,subscriptions)
        topic_arn = create_TnS.create_topic_and_sub()
        print("Topic arn is " + topic_arn)

       
        # Create Alarms for each metrics
        for metric in metrics:
          if metric in tags_list and metric in client.list_queue_tags(QueueUrl=self.queue.url)[u'Tags']:
              thresholds[metric]["threshold"] = client.list_queue_tags(QueueUrl=self.queue.url)[u'Tags'][metric]
          else:
              print(metric + " not defined in tags, so picking up default value")

          
          # If perecent is defined in threshold, threshold will be % of source
          # Like threshold is "75 percent" for ApproximateAgeOfOldestMessage, threshold set will be 75% of MessageRetentionPeriod
          if "percent" in thresholds[metric]["threshold"]:
              source = self.queue.attributes[thresholds[metric]["source"]]
              print(thresholds[metric]["source"] + " set for queue " + queue_name + " is " + source)
              percent = thresholds[metric]["threshold"].replace('percent','').replace(' ','')
              print("Threshold %age set for queue " + queue_name + " will be " + percent + "% of " + thresholds[metric]["source"])
              thresholds[metric]["threshold"] = int(source)*int(percent)//100
              print("Setting threshold value to " + str(thresholds[metric]["threshold"]) + thresholds[metric]["unit"])

          create_alarm = create_alarms.create_alarms("SQS","QueueName",queue_name,metric,thresholds[metric]["operator"],thresholds[metric]["threshold"],thresholds[metric]["unit"],topic_arn)
          create_alarm.create_cloudwatch_alarms()
