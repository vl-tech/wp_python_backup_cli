#!/usr/bin/env python3
from paramiko import SSHClient
import paramiko
import  sys
import argparse
import os
from datetime import datetime
import time
from pprint import pprint
import sqlite3
import argcomplete
from pprint import pprint
from collections import OrderedDict
_date = datetime.today()
current_date = _date.strftime("%d-%m-%Y")
port = 12545


# (self.password,self.wordpress_path,self.username,self.domain_name)
parser = argparse.ArgumentParser(prog='WordPress Backup tools',description='Backing up WP Remote via SSH Paramiko')

parser.add_argument('-u','--user',action='store',help='-u username of cPanel')
parser.add_argument('-p','--password',action="store",help='-p add password for cPanel')
parser.add_argument('-d','--domain',action="store",help='-d domain for cPanel')
parser.add_argument('-P','--path',action="store",help='-P domain path for cPanel')
parser.add_argument('-H','--host',action="store",help='-H hostname for cPanel')
# parser.add_argument('-R','--restore',action="store",help='-R Restore Added Wordpress Site From database')
# parser.add_argument('-D','--wp_site',action='store',help='-D/--wp-site Provider domain argument <domain>/<wp_sute>')

parser.add_argument('--action',choices=['backup','restore','add_website','delete_website','list_website','all_sites',
                                        'check','restore2','list_website2','backup2'],default='check')
argcomplete.autocomplete(parser)

args = parser.parse_args()

exclude_path = ("./wp-content/uploads")

# class WpDatabase():
connection = sqlite3.connect(database='wordpress_support.db')
class WpDatabase:
    def __init__(self,domain_name,username,password,hostname,wp_path,backup_folder):
        self.domain_name = domain_name
        self.username = username
        self.password = password
        self.hostname = hostname
        self.wp_path = wp_path
        self.backup_folder = backup_folder
        
    def add_website(self):
        add_new_website = f"""
        INSERT INTO wordpress_sites(domain_name,username,password,hostname,wp_path,backup_folder)
        VALUES('{self.domain_name}',
        '{self.username}',
        '{self.password}',
        '{self.hostname}',
        '{self.wp_path}',
        '{self.backup_folder}')

        """ 
        return  add_new_website


    # Key issue with deleting a website was to set the variable in single quotes. Otherwise error was present:
    # The error was sqlite3.OperationalError: no such column: python.vladmin.top
    # EXplicitly MySQL and SQLITe work with quotes for each element
    
    def delete_wp_site(self):
        delete_website = f"""
        DELETE from wordpress_sites WHERE domain_name='{self.domain_name}';

        """
        return delete_website
    
    # Lists A awebsites selected on the command line with --action list_website
    def show_site_data(self):
        website_data = f"""
                SELECT * FROM wordpress_sites WHERE domain_name='{self.domain_name}'
        """
       
        return website_data   
    
    # Listing ALL websites that were added to the database             
    def list_all_websites(self):
        list_website = """
        select * from wordpress_sites;

        """
        return list_website
        
        
        
class WordPressBackup:
    def __init__(self):
        self.username = args.user
        self.password  = args.password
        self.hostname = args.host
        self.wordpress_path = args.path
        self.domain_name = args.domain
        self.backup_folder =  f'{self.domain_name}_backup_folder_{current_date}'
        self.backup_tar_file = f"{self.backup_folder}/{self.domain_name}-backup{current_date}.tar.gz"
        self.database_backup_file = f"{self.backup_folder}/{self.domain_name}-backup-{current_date}.sql"
        
    def connect_to_host(self):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname,port,self.username, self.password)
        
        return f"Connection to {self.hostname} Was SuccessFull",client
        
        
        
        
    def create_backup(self):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname,port,self.username, self.password)
        client.exec_command(f'mkdir {self.backup_folder}')
        time.sleep(2)
        print("#"*50)
        print('Backup Folder successfull created ')
        print("#"*50)
        print('Starting Creation of Database backup and Files Backup ')
        print("#"*50)
        print("...")
        # RUN COMMAND SSH
       
        backup_wordpress = client.exec_command(f"wp --path={self.wordpress_path} db export {self.database_backup_file} && tar --exclude='{exclude_path}'-czf  {self.backup_tar_file} -C {self.wordpress_path} .")
        stdin, stdout, stderr = backup_wordpress
        print("#"*50)
        print(stdout.read().decode('utf-8'))
        print("#"*50)
        print(stderr.read().decode('utf-8'))
        
        time.sleep(2)
        
        print('Process of Backup finished successfully')
        print("#"*50)
        print()
        print("Listing backup folder!")
        print()
        print("#"*50)
        
        backup_folder_list = client.exec_command(f"ls -al {self.backup_folder}")
        stdin , dir_list,stderr = backup_folder_list
        print("#"*50)
        print()
        print(dir_list.read().decode('utf-8'))
        print("#"*50)
        
        return  {"Connection":"Connection Successfulll",
                "Folder":f"Backup Folder Created {self.backup_folder}"
            } ,sys.exit('End of Program! Bye Bye')
        
      
    def check_backup_folder(self):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname,port,self.username, self.password)
        backup_folder_files = client.exec_command(f'ls  {self.backup_folder}')
        stdin ,stdout, stderr = backup_folder_files
        output = stdout.read().decode('utf-8')
        if stderr.read().decode('utf-8') != "":
            client.exec_command(f'mkdir {self.backup_folder}')
            print("#"*50)
            print()
            return "Backup Folder was created",stderr.read().decode('utf-8')
        else:
            print("#"*50)
            print()
            print("Backup Folder Already Exists:")
            print(f"############## {self.backup_folder} ############## ")
            print()      
            print('Listing Backup folder content')
            print(f'{output}')
            print("#"*50)
            print()

            return "End of script. Rerun the script to generate or restore a backup"
        # return "Backup Was restored",stderr.read().decode('utf-8')
        
        
        
        
    def restore_backup(self,):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname,port,self.username, self.password)
        print(f"Exporting the files from {self.backup_tar_file} to {self.wordpress_path}")
        restore_command = client.exec_command(f'tar -xzf {self.backup_tar_file} -C {self.wordpress_path}')
        delete_current_content = client.exec_command(f'rm -rf {self.wordpress_path}/*')
        i,o,e = delete_current_content
        print(f'Deleting files and folders inside WP DIR {self.wordpress_path}')
        print(o.read().decode('utf-8'))
        print(e.read().decode('utf-8'))
        stdin ,stdout, stderr = restore_command
        print(stdout.read().decode('utf-8'))
        print("#"*50)
        print('File restore completed! Continuing with database import')
        print("#"*50)
        print(f'Starting Database {self.database_backup_file} import process! ')
        print("#"*50)
        print("#"*50)
        database_restore_command = client.exec_command(f'wp --path={self.wordpress_path} db import {self.database_backup_file}')
        stdin ,stdout, stderr = database_restore_command
        print(stdout.read().decode('utf-8'))
        print("#"*50)
        print()
        print('Database Import Completed Successfully')


class BackupFromDatabase:
    def __init__(self,username,password,hostname,wordpress_path,domain_name):
        self.username = username
        self.password  = password
        self.hostname = hostname
        self.wordpress_path = wordpress_path
        self.domain_name = domain_name
        self.backup_folder =  f'{self.domain_name}_backup_folder_{current_date}'
        self.backup_tar_file = f"{self.backup_folder}/{self.domain_name}-backup{current_date}.tar.gz"
        self.database_backup_file = f"{self.backup_folder}/{self.domain_name}-backup-{current_date}.sql"
        

    def do_backup(self):
        
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname,port,self.username, self.password)
        client.exec_command(f'mkdir {self.backup_folder}')
        time.sleep(2)
        print("#"*50)
        print('Backup Folder successfull created ')
        print("#"*50)
        print('Starting Creation of Database backup and Files Backup ')
        print("#"*50)
        print("...")
        # RUN COMMAND SSH
        
        print("Excluding Uploads folder from, the backup")
        print(exclude_path)
        backup_wordpress = client.exec_command(f"wp --path={self.wordpress_path} db export {self.database_backup_file} && tar --exclude='{exclude_path}' --exclude-backups -czf  {self.backup_tar_file} -C {self.wordpress_path} .")
        stdin, stdout, stderr = backup_wordpress
        print("#"*50)
        print(stdout.read().decode('utf-8'))
        print("#"*50)
        print(stderr.read().decode('utf-8'))
        
        time.sleep(2)
        
        print('Process of Backup finished successfully')
        print("#"*50)
        print()
        print("Listing backup folder!")
        print()
        print("#"*50)
        
        backup_folder_list = client.exec_command(f"ls -al {self.backup_folder}")
        stdin , dir_list,stderr = backup_folder_list
        print("#"*50)
        print()
        print(dir_list.read().decode('utf-8'))
        print("#"*50)
        
        return  {"Connection":"Connection Successfulll",
                "Folder":f"Backup Folder Created {self.backup_folder}"
            } ,sys.exit('End of Program! Bye Bye')
        
    def restore_backup(self):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname,port,self.username, self.password)
        print(f"Exporting the files from {self.backup_tar_file} to {self.wordpress_path}")
        restore_command = client.exec_command(f"tar  -xzf {self.backup_tar_file} -C {self.wordpress_path}")
        delete_current_content = client.exec_command(f'rm -rf {self.wordpress_path}/*')
        i,o,e = delete_current_content
        print(f'Deleting files and folders inside WP DIR {self.wordpress_path}')
        print(o.read().decode('utf-8'))
        print(e.read().decode('utf-8'))
        stdin ,stdout, stderr = restore_command
        print(stdout.read().decode('utf-8'))
        print("#"*50)
        print('File restore completed! Continuing with database import')
        print("#"*50)
        print(f'Starting Database {self.database_backup_file} import process! ')
        print("#"*50)
        print("#"*50)
        database_restore_command = client.exec_command(f'wp --path={self.wordpress_path} db import {self.database_backup_file}')
        stdin ,stdout, stderr = database_restore_command
        print(stdout.read().decode('utf-8'))
        print("#"*50)
        print()
        print('Database Import Completed Successfully')

if __name__ == "__main__":
    # First Instance for main Actions backup,restore,check
    main_backup = WordPressBackup()
    # Secibd ubstance for utilizing the databases with the main class Variables
    db_variables = WordPressBackup()
    # db_instance Registers the website data into the database
    db_instance = WpDatabase(db_variables.domain_name,db_variables.username,db_variables.password,db_variables.hostname,db_variables.wordpress_path,db_variables.backup_folder)
    # Creating the Database cursor object
    cursor = connection.cursor()
    
    
    if args.action == 'restore':
        print(main_backup.connect_to_host())
        print(main_backup.restore_backup())
    elif args.action == 'backup':
        print("#"*50)
        print(main_backup.create_backup())
    elif args.action == 'add_website':
        print("#"*50)
        print(f'Website {db_variables.domain_name} was added successfully')
        print("To list available websites run with --action list_website <website name> ")
        cursor.execute(db_instance.add_website())
        connection.commit()
        connection.close()
    elif args.action == 'delete_website':
         print("#"*50)
         print(f"Website -- {db_variables.domain_name} -- was deleted successfully")
         cursor.execute(db_instance.delete_wp_site())
         connection.commit()
         connection.close()
    elif args.action == 'list_website':
        cursor.execute(db_instance.show_site_data())
        site_data = cursor.fetchall()
        
        wp_site_details = {'domain_name':site_data[0][1],
            'username':site_data[0][2],
            'password':site_data[0][3],
            'hostname':site_data[0][4],
            'wp_path':site_data[0][5],
            'backup_folder':site_data[0][6],
            }
        pprint(OrderedDict(wp_site_details))
        
    elif args.action == 'all_sites':
        cursor.execute(db_instance.list_all_websites())
        list_all_websites = cursor.fetchall()
        for site in list_all_websites:
            print(site)
        connection.close()
        
    
    elif args.action == 'list_website2':
        cursor.execute(db_instance.show_site_data())
        db_site_data = cursor.fetchall()
        domain_name = db_site_data[0][1]
        user = db_site_data[0][2]
        password = db_site_data[0][3]
        hostname = db_site_data[0][4]
        wordpress_path = db_site_data[0][5]
        
        print(f"Domain Name: {domain_name}")
        print(f"cPanel Username: {user}")
        print(f"IP: {hostname}")
        print(f"Path to WP installation: {wordpress_path}")
        print(f"cPanel Password: {password}")
        
    elif args.action == "backup2":
        cursor.execute(db_instance.show_site_data())
        db_site_data = cursor.fetchall()
        domain_name = db_site_data[0][1]
        user = db_site_data[0][2]
        password = db_site_data[0][3]
        hostname = db_site_data[0][4]
        wordpress_path = db_site_data[0][5]
        backup_instance = BackupFromDatabase(user,password,hostname,wordpress_path,domain_name)
        print(backup_instance.do_backup())
        
    elif args.action == 'restore2':
        cursor.execute(db_instance.show_site_data())
        db_site_data = cursor.fetchall()
        domain_name = db_site_data[0][1]
        user = db_site_data[0][2]
        password = db_site_data[0][3]
        hostname = db_site_data[0][4]
        wordpress_path = db_site_data[0][5]
        backup_instance = BackupFromDatabase(user,password,hostname,wordpress_path,domain_name)
        print(backup_instance.restore_backup())
    # elif args.action == "list_website":
    #     cursor.execute(db_instance.show_site_data())
    #     site_data = cursor.fetchall()
    #     # db_data = BackupFromDatabase(user,password,hostname,wordpress_path)
    #     # cursor.execute(db_data.fetch_variables())
        
        
        
    else:
        print(main_backup.check_backup_folder())
    #from_db_restore','from_db_list','from_db_backup'
    
    
    
    