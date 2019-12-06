import hashlib
import time
import math
import boto3


def findGoldenNonce(dif, t, ntotal, nhost):
    sqs = boto3.resource('sqs', 'us-east-1',
                         aws_access_key_id='',
                         aws_secret_access_key='',
                         aws_session_token=''
                         )
    queue = sqs.get_queue_by_name(QueueName='test')

    data = 'COMSM0010cloud'
    total = int(ntotal)
    task_index = int(nhost)
    difficulty = int(dif)
    golden_str = difficulty * '0'
    total_range = int(math.pow(2, 32))
    block_length = int(total_range / total)
    lower_bound = block_length * task_index
    upper_bound = 0
    if task_index == total - 1:
        upper_bound = total_range
    else:
        upper_bound = block_length * (task_index + 1)

    start_time = time.time()
    for i in range(lower_bound, upper_bound):
        temp = bin(i)
        C_data = ''.join(format(i, 'b') for i in bytearray(data, encoding='utf-8'))
        value_before_hash = temp + C_data
        first_hash = hashlib.sha256(value_before_hash.encode('utf-8')).hexdigest()
        second_hash = hashlib.sha256(first_hash.encode('utf-8')).hexdigest()

        if second_hash.startswith(golden_str, 0, difficulty):
            print("Instance " + str(task_index) + " " + "Successfully find a golden nonce: " + str(i))
            print("--- %s seconds ---" % (time.time() - start_time))
            send_message = str(i) + " " + str(time.time() - start_time)
            queue.send_message(MessageBody=send_message)
            print("finshed without time out")
            break

        if time.time() - start_time > int(t):
            print("time out" + "run time: " + str(time.time()- start_time))
            break







if __name__ == "__main__":
    #get the message from the sqs
    sqs_client = boto3.client('sqs', region_name = 'us-east-1',
                              aws_access_key_id='',
                              aws_secret_access_key='',
                              aws_session_token=''
                              )
    queue_url = 'https://sqs.us-east-1.amazonaws.com/242085349695/test'
    response = sqs_client.receive_message(QueueUrl=queue_url)
    recv_message = response['Messages'][0]
    receipt_handle = recv_message['ReceiptHandle']
    n_vm, dif, run_time, index = recv_message['Body'].split()
    #print("n_v: " + n_vm + " " + "dif: " + dif + " " + "run_time: " + run_time + " " + "index: " + index )

    sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    findGoldenNonce(dif, run_time, n_vm, index)
