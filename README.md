# networks-project
 50.012 Networks Course Project


## Setup
Currently tested for AWS Linux on EC2 instance

1. Import all files into an EC2 AWS Linux instance (e.g WinSCP)
2. Run `sudo bash setup.sh` (Bash commands currently utilizing yum as package manager, modify to fit your distro)
3. Add your AWS CLI credentials inside the 'credentials' file
4. In 'config.sh', modify the 'lb_instanceID' variable to contain the AWS instance ID of the load balancer EC2 instance.
5. Run 'sudo bash config.sh'
6. Depending on whether or not the instance is meant to be a load balancer or a server, run 'python3.12 lb.py' or 'python3.12 server.py'