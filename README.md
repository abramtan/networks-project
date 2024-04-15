# networks-project
 50.012 Networks Course Project


## Setup
Currently tested for AWS Linux on EC2 instance

1. Import all files into an EC2 AWS Linux instance (e.g WinSCP)
2. Run `sudo bash setup.sh` (Bash commands currently utilizing yum as package manager, modify to fit your distro)
3. Add your AWS CLI credentials inside the 'credentials' file
4. In 'config.sh', modify the 'lb_instanceID' variable to contain the AWS instance ID of the load balancer EC2 instance.
5. Run 'sudo bash config.sh'
- Ensure that config.py has the correct IP address for loadbalancer
6. Depending on whether or not the instance is meant to be a load balancer or a server, run 'python3.12 lb.py --mode [rr/connections/power/ic]' or 'python3.12 server.py'
7. With both a running instance of a server and a load balancer, run the client application either on an EC2 instance of locally (Ensure config.py has load balancer IP)