#!/usr/bin/env python3

import subprocess
from paramiko import SSHClient
import paramiko
import  sys
import argparse
from datetime import datetime
import time
from pprint import pprint


_date = datetime.today()


current_date = _date.strftime("%d-%m-%Y")
cmd = '`eval ssh-agent`'
turn_on_ssh_agent = subprocess.run(cmd,shell=True)
print(turn_on_ssh_agent)
parser = argparse.ArgumentParser(prog='WordPress Backup tools',description='Backing up WP Remote via SSH Paramiko')


parser.add_argument('-u','--user',action='store',help='-u username of cPanel')
# parser.add_argument('-p','--password',action="store",help='-p add password for cPanel')
parser.add_argument('-d','--domain',action="store",help='-d domain for cPanel')
parser.add_argument('-P','--path',action="store",help='-P domain path for cPanel')
parser.add_argument('-H','--host',action="store",help='-H hostname for cPanel')
parser.add_argument('-R','--restore',action="store",help='-R Restore Wordpress Website ')
parser.add_argument('-R','--restore',action="store",help='-R Restore Wordpress Website ')
args = parser.parse_args()

username = args.user
# pw = args.password
domain = args.domain
dompath = args.path
hostname = args.host


# user = 'vladmint'
pw = "Vladimir1987!@"
# IP ="185.199.38.18"
# host = 'vladmin.top'
port = 12545
# key_file = paramiko.rsakey.RSAKey(filename='id_rsa')

client = SSHClient()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname,port,username, pw)
# CREATE BACKUP FOLDER
backup_folder = f'{domain}_backup_{current_date}'

client.exec_command(f'mkdir {backup_folder}')
time.sleep(2)
print('Backup Folder successfull created ')
print('Starting Creation of Database backup and Files Backup ')
print("...")
# RUN COMMAND SSH
backup_wordpress = client.exec_command(f"wp --path={dompath} db export {backup_folder}/{domain}-backup-{current_date}.sql && tar -czf {backup_folder}/{domain}-backup{current_date}.tar.gz {dompath}")

stdin, stdout, stderr = backup_wordpress

print(stdout.read())
# print(stderr.read())
time.sleep(2)
print('Process of Backup finished successfully')
print("#"*30)
print("Listing backup folder!")
print("#"*30)
backup_folder_list = client.exec_command(f'ls -alhS {backup_folder}')
stdin , dir_list,stderr = backup_folder_list
pprint(f'{dir_list.read()}')
sys.exit('End of Program! Bye Bye')
# output = stdout.readlines()