import boto3
import time


client = boto3.client('ec2')
ec2 = boto3.resource('ec2',)
sqs = boto3.resource('sqs')
sqs_client = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/242085349695/test'
ubuntu_id = 'ami-04b9e92b5572fa0d1'
type='t2.micro'

#submit the python task file to the S3 bucket
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket_name = 'this-is-my-python'
# client.create_bucket(Bucket='this-is-my-python')
filename1 = 'demo1.py'
s3_client.upload_file(filename1, bucket_name, filename1,ExtraArgs={'ACL':'public-read'})


#read in the user specified parameters
queue = sqs.get_queue_by_name(QueueName='test')
N_machine = input("type the numebr of machine you want")
dif = input("type the dif")
run_time = input("type the max run time")

counter = 0
for i in range(0, int(N_machine)):
    send_message = str(N_machine) + " " + str(dif) + " " + str(run_time) + " " + str(counter)
    queue.send_message(MessageBody=send_message)
    counter += 1

#give time to SQS to initialize
time.sleep(5)

#create instance with userdata where the user data is written in startup.sh
user_data = open('startup.sh').read()
instance = ec2.create_instances(ImageId = ubuntu_id, MinCount = int(N_machine),
                                MaxCount = int(N_machine),
                                KeyName = 'new_EC2',
                                SecurityGroups = ['launch-wizard-11'],
                                InstanceType = type,
                                UserData = user_data)

#give instances enough time to initialize
#which includes install pip3, boto3
#this value is not really constant, depends on the network
#sometime it requires longer time to initial the environment
#so just in case I set it to a huge number for that
time.sleep(360)

start_time = time.time()
#using a infinite while loop to check the run time and if over the time limit then terminate all the instances

#******notice there can be a situation that some instances setup late and some ones
# have already return the message which will be accessed by the late instance which
# will block the instance. If the result gives 4 values then it means some of the instances
# have been blocked
while True:
    #everytime run the while loop, it will
    end_time = time.time()
    resp = sqs_client.receive_message(
        QueueUrl=queue_url
    )
    try:
        message = resp['Messages'][0]
        print(message['Body'])
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        for instance in instances:
            ec2.instances.filter(InstanceIds=[instance.id]).terminate()
        break
    except KeyError:
        message = []

    if end_time - start_time < int(run_time):
        continue
    if end_time - start_time > int(run_time):
        print("time out no golden nonce found")
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        for instance in instances:
            ec2.instances.filter(InstanceIds=[instance.id]).terminate()
        break




