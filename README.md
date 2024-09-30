# Remote WordPress Backup tool
- The tool uses Paramiko SSH module of python to connect to the remote machine.
- Along with that it has Sqlite3 module that stores the data for Host , username , password and WP path 
- It takes those details and connects to the remote host and creates a backup of the wordpress files and database.
- In order to work . The remote server must have SSH enabled + password authentication
- Port is hardcoded into the script for this version of the tool.
- WP database backup requires wp-cli to be installed on the server for the user that we are connecting with.
- mysqldump can be embedded as an option later on , but for now It uses just wp-cli

# NB!!! The script does not backup wp-content/uploads folder to reduce backup and restore times.
## Remember to not delete anything from your uploads folder or have a separate backup for it
## The tool supports Backup and Restores of currently created backup
## Arguments/Legend
```bash
/wp_backup.py -h
##################################################

EXAMPLE COMMAND TO ADD WEBSITE TO DATABASE

./wp_backup.py --action add_website -u cPanel UserName -d python.vladmin.top -P wordpress-folder-path (Without back slash/ example.com or /home/user/example.com) -p 'PASSWORD' ( Always in single quotes to prevent parameter expansion! ) -H HOST/IP

##################################################
usage: WordPress Backup tools [-h] [-u USER] [-p PASSWORD] [-d DOMAIN] [-P PATH] [-H HOST]
                              [--action {backup,restore,add_website,delete_website,list_website,all_sites,check,restore2,list_website2,backup2}]

Backing up WP Remote via SSH Paramiko

options:
  -h, --help            show this help message and exit
  -u USER, --user USER  -u username of cPanel
  -p PASSWORD, --password PASSWORD
                        -p add password for cPanel
  -d DOMAIN, --domain DOMAIN
                        -d domain for cPanel
  -P PATH, --path PATH  -P domain path for cPanel
  -H HOST, --host HOST  -H hostname for cPanel
  --action {backup,restore,add_website,delete_website,list_website,all_sites,check,restore2,list_website2,backup2}

```
 - The tool is designed initial to utilize cPanel+SSH Password authentication and cpanel folder structure
 - It will work for any SSH available connection server that it has wp-cli and a wordpress website

## Example commands
1. Add Website to the database file 
```bash
./wp_backup.py --action add_website -u SSH_USERNAME -p 'PASSWORD' -H IP/Hostname -d domain_name -P WP_PATH 
```
2. Delete a Website and its credentials from the database


```bash
./wp_backup.py --action delete_website -d website_name/domain_name

```

3. Version one --action backup option
 - It takes all arguments from the command line and does not add the site to the database
 - Example

```bash
/wp_backup.py --action backup -u SSH_USERNAME -p 'PASSWORD' -d domain_name/websitename -P /home/path/to/wp -H IP/Hostname

```

4. Restore option is the same --action restore 

```bash
/wp_backup.py --action restore -u SSH_USERNAME -p 'PASSWORD' -d domain_name/websitename -P /home/path/to/wp -H IP/Hostname

```
5. Default no argument action is to check whether there is a backup folder and a backup from today. It does not support backups for older dates
 - It will throw paramiko.ssh_exception.NoValidConnectionsError and display the usage
```bash
./wp_backup.py

./wp_backup.py --action add_website -u ssh_UserName -d website_name.com 
-P wordpress-folder-path 
(Without back slash/ example.com or /home/user/example.com) 
-p 'PASSWORD' ( Always in single quotes to prevent parameter expansion! ) -H HOST/IP
```

6. List a specific website name or all sites

```bash
./wp_backup.py --action all_sites

(6, 'None', 'vl-tech', 'SOME PASS', '192.168.1.2', '/home/wp_site', 'None_backup_folder_30-09-2024')

```
 - If you forget to add -d domain name you can delete it with the same command but with delete option

```bash
./wp_backup.py --action delete_website -u vl-tech -H 192.168.1.2 -p 'SOME PASS' -P /home/wp_site

```

- Correct command template 

```bash
./wp_backup.py --action add_website -u vl-tech -H 192.168.1.2 -p 'SOME PASS' -P /home/wp_site -d example_website.com

```

- Showing the website details from the database 

```bash
./wp_backup.py --action list_website2 -d example_website.com
##################################################

EXAMPLE COMMAND TO ADD WEBSITE TO DATABASE

./wp_backup.py --action add_website -u ssh_UserName -d website_name.com -P wordpress-folder-path (Without back slash/ example.com or /home/user/example.com) -p 'PASSWORD' ( Always in single quotes to prevent parameter expansion! ) -H HOST/IP

##################################################
Domain Name: example_website.com
SSH Username: vl-tech
IP: 192.168.1.2
Path to WP installation: /home/wp_site
SSH Password: SOME PASS

```
- Listing method 1 will fetch data from  the database in  unformatted way

```bash
/wp_backup.py --action list_website -d example_website.com
##################################################

EXAMPLE COMMAND TO ADD WEBSITE TO DATABASE

./wp_backup.py --action add_website -u ssh_UserName -d website_name.com -P wordpress-folder-path (Without back slash/ example.com or /home/user/example.com) -p 'PASSWORD' ( Always in single quotes to prevent parameter expansion! ) -H HOST/IP

##################################################
OrderedDict([('domain_name', 'example_website.com'),
             ('username', 'vl-tech'),
             ('password', 'SOME PASS'),
             ('hostname', '192.168.1.2'),
             ('wp_path', '/home/wp_site'),
             ('backup_folder', 'example_website.com_backup_folder_30-09-2024')])
```

## Most viable option is backup2 and restore2
- It takes a website from the database and creates a backup for it

- BACKUP
```bash
./wp_backup.py --action backup2 -d example_website.com
```
- RESTORE
```bash
 ./wp_backup.py --action restore2 -d example_website.com
```


