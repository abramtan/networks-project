import os
import sys
import boto3
from pprint import pprint

local_directory = './dash/test-8'
bucket = 'networks-project-s3-bucket'
destination = 'test-8_1'

client = boto3.client('s3')

for root, dirs, files in os.walk(local_directory):

  for filename in files:

    local_path = os.path.join(root, filename)
    relative_path = os.path.relpath(local_path, local_directory)
    s3_path = os.path.join(destination, relative_path)

    print('Searching "%s" in "%s"' % (s3_path, bucket))
    try:
        response = client.head_object(Bucket=bucket, Key=s3_path)
        print("Path found on S3! Skipping %s..." % s3_path)
    except:
        print("Uploading %s..." % s3_path)
        response = client.upload_file(local_path, bucket, s3_path, ExtraArgs={'ACL':'public-read'})
    pprint(response)

print(f'Done uploading. Access video here: https://networks-project-s3-bucket.s3.amazonaws.com/{destination}/BigBuckBunny.m3u8')