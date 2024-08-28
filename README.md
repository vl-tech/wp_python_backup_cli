# Remote WordPress Backup tool
- The tool uses Paramiko SSH module of python to connect to the remote machine.
- Along with that it has Sqlite3 module that stores the data for Host , username , password and WP path 
- It takes those details and connects to the remote host and creates a backup of the wordpress files and database.
- In order to work . The remote server must have SSH enabled + password authentication
- Port is hardcoded into the script for this version of the tool.
- WP database backup requires wp-cli to be installed on the server for the user that we are connecting with.
- mysqldump can be embedded as an option later on , but for now It uses just wp-cli
## The tool supports Backup and Restores of currently created backup
