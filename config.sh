#!/bin/bash

lb_instanceID=

HOME=/home/ec2-user
cp credentials /home/ec2-user/.aws
aws configure set output "text" --profile temp
aws configure list 

dns_hostname=$(curl http://169.254.169.254/latest/meta-data/public-hostname/)
lb_hostname=$(aws ec2 describe-instances --instance-ids $lb_instanceID --query 'Reservations[].Instances[].PublicDnsName | [0]')

printf '' > config.py
echo -e 'hostIP =' "'$dns_hostname'"  >> config.py
echo 'lbIP = ' "$lb_hostname" >> config.py
#echo ${dns_hostname}
