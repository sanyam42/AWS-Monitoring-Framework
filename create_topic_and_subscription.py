import boto3
sns = boto3.client('sns')

class create_topic_and_subscription:
    def __init__(self, topic_name, subscriptions):
                    self.topic_name = topic_name
                    self.subscriptions = subscriptions


    def create_topic_and_sub(self):
        
        # Creating Topic which is picked from tag Owner
        print("Creating topic " + self.topic_name)
        response = sns.create_topic(Name=self.topic_name)
        topic_arn = response[u'TopicArn']

       
        # Get list of all Current Subscriptions fot the topic
        response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        curr_subscriptions = {}
        for sub in response[u'Subscriptions']:
            curr_subscriptions[sub[u'Endpoint']] = sub[u'SubscriptionArn']

        print("Current Subscriptions are " + str(curr_subscriptions))

        # If email is not in Current Subscriptions list, subscription will be created. If subscription exists but status is PendingConfirmation, notification will be sent on email.
        for subscription in self.subscriptions.split():
            if (subscription in curr_subscriptions and curr_subscriptions[subscription] != "PendingConfirmation"):
                print(subscription + " already subscribed for topic " + self.topic_name)
            else:
                print("Creating subscription for email " + subscription + " for topic " + self.topic_name)
                response = sns.subscribe(
                    TopicArn=topic_arn,
                    Protocol='email',
                    Endpoint=subscription,
                    ReturnSubscriptionArn=True
                )

        return topic_arn

