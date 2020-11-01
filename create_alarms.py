import boto3
cw = boto3.client('cloudwatch')

# Create Cloudwatch alarms
class create_alarms:
    def __init__(self, service_type, dimensions_name, dimensions_value, metric, operator, threshold, unit, topic_arn):
                    self.service_type = service_type
                    self.dimensions_name = dimensions_name
                    self.dimensions_value = dimensions_value
                    self.metric = metric
                    self.operator = operator
                    self.threshold = threshold
                    self.topic_arn = topic_arn
                    self.unit = unit


    def create_cloudwatch_alarms(self):

        print("Threshold for metric " + self.metric + " is " + str(self.threshold))

        alarm_name = self.service_type + "_" + self.dimensions_value + "_" + self.metric
        namespace = "AWS/" + self.service_type

        cw.put_metric_alarm(
            AlarmName=alarm_name,
            ComparisonOperator=self.operator,
            EvaluationPeriods=1,
            MetricName=self.metric,
            Namespace=namespace,
            Period=60,
            Statistic='Average',
            Threshold=int(self.threshold),
            Dimensions=[
                {
                  'Name': self.dimensions_name,
                  'Value': self.dimensions_value
                },
            ],
            ActionsEnabled=True,
            AlarmActions=[self.topic_arn],
            Unit=self.unit
        )

