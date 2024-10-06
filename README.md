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

./wp_backup.py --action add_website -u SSH_UserName -d website_name.com -P wordpress-folder-path (Without back slash/ website_name.com or /home/user/website_name.com) -p 'PASSWORD' ( Always in single quotes to prevent parameter expansion! ) -H HOST/IP

##################################################
usage: WordPress Backup tools [-h] [-u USER] [-p PASSWORD] [-d DOMAIN] [-P PATH] [-H HOST]
                              [--action {backup,restore,add_website,delete_website,list_website,all_sites,check,restore2,list_website2,backup2}]

Backing up WP Remote via SSH Paramiko

options:
  -h, --help            show this help message and exit
  -u USER, --user USER  -u username of SSH
  -p PASSWORD, --password PASSWORD
                        -p add password for SSH
  -d DOMAIN, --domain DOMAIN
                        -d domain for SSH
  -P PATH, --path PATH  -P domain path for SSH
  -H HOST, --host HOST  -H hostname for SSH
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


## Install completion for the Python Script

```ruby
sudo pip install 'argcomplete>=0.5.7'
```

# For global activation of all argcomplete enabled python applications run:


```ruby
sudo activate-global-python-argcomplete
```

# For permanent (but not global)`pytest`activation, use:

```ruby
register-python-argcomplete pytest >> ~/.bashrc
```

# For one-time activation of argcomplete for`pytest`only, use:

```ruby
eval "$(register-python-argcomplete pytest)"
```
## If the above methods do not work just add the below code to your bashrc at the end

```bash
# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
#if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
#    . /etc/bash_completion
#fi


# Run something, muting output or redirecting it to the debug stream
# depending on the value of _ARC_DEBUG.
# If ARGCOMPLETE_USE_TEMPFILES is set, use tempfiles for IPC.
__python_argcomplete_run() {
    if [[ -z "${ARGCOMPLETE_USE_TEMPFILES-}" ]]; then
        __python_argcomplete_run_inner "$@"
        return
    fi
    local tmpfile="$(mktemp)"
    _ARGCOMPLETE_STDOUT_FILENAME="$tmpfile" __python_argcomplete_run_inner "$@"
    local code=$?
    cat "$tmpfile"
    rm "$tmpfile"
    return $code
}

__python_argcomplete_run_inner() {
    if [[ -z "${_ARC_DEBUG-}" ]]; then
        "$@" 8>&1 9>&2 1>/dev/null 2>&1
    else
        "$@" 8>&1 9>&2 1>&9 2>&1
    fi
}

_python_argcomplete() {
    local IFS=$'\013'
    local SUPPRESS_SPACE=0
    if compopt +o nospace 2> /dev/null; then
        SUPPRESS_SPACE=1
    fi
    COMPREPLY=( $(IFS="$IFS" \
                  COMP_LINE="$COMP_LINE" \
                  COMP_POINT="$COMP_POINT" \
                  COMP_TYPE="$COMP_TYPE" \
                  _ARGCOMPLETE_COMP_WORDBREAKS="$COMP_WORDBREAKS" \
                  _ARGCOMPLETE=1 \
                  _ARGCOMPLETE_SUPPRESS_SPACE=$SUPPRESS_SPACE \
                  __python_argcomplete_run "$1") )
    if [[ $? != 0 ]]; then
        unset COMPREPLY
    elif [[ $SUPPRESS_SPACE == 1 ]] && [[ "${COMPREPLY-}" =~ [=/:]$ ]]; then
        compopt -o nospace
    fi
}
complete -o nospace -o default -o bashdefault -F _python_argcomplete wp_backup.py
```

## For Centos7 use the same bashrc code but it requires a few more packages to be installed
1. Fix the Repositories
```bash
curl -o /etc/yum.repos.d/CentOS-Base.repo https://el7.repo.almalinux.org/centos/CentOS-Base.repo

```
- Using the almalinux repos from the almalinux elevate tutorial 
- https://wiki.almalinux.org/elevate/ELevating-CentOS7-to-AlmaLinux-9.html#upgrade-centos-7-to-almalinux-8

2. Update the repos
```bash
yum -y update  
```

3. Install argcomplete and virtualenv and upgrade pip

```bash
yum -y install python3-argcomplete

yum -y install python3-argcomplete

pip3 install --upgrade pip
```

