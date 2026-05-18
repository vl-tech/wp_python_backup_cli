# Remote WordPress Backup Tool

- Uses Paramiko SSH module to connect to the remote machine.
- Uses SQLite3 to store site credentials (hostname, username, password, WP path).
- Connects via SSH and creates a backup of WordPress files and database.
- Remote server must have SSH + password authentication enabled.
- WP database backup requires **wp-cli** installed on the remote server for the connecting user.

> **Note:** `wp-content/uploads` is excluded from backups to reduce backup and restore times.
> Keep a separate backup of your uploads folder.

---

## Installation

Installs dependencies via `apt` (Ubuntu/Debian):

```bash
make install
```

To also set up shell autocomplete interactively:

```bash
make all
# or separately:
make autocomplete
```

---

## Arguments

```
usage: WordPress Backup Tools [-h] [-u USER] [-p PASSWORD] [-d DOMAIN]
                              [-P PATH] [-H HOST] [-i ID] [--port PORT]
                              [--trust-host]
                              [--action {backup,restore,add_website,
                                         delete_website,list_website,
                                         all_sites,check,
                                         backup_db,restore_db,list_website_db}]

options:
  -h, --help            show this help message and exit
  -u USER, --user USER  SSH username
  -p PASSWORD, --password PASSWORD
                        SSH password (use single quotes)
  -d DOMAIN, --domain DOMAIN
                        Domain name
  -P PATH, --path PATH  WordPress installation path (no trailing slash)
  -H HOST, --host HOST  Hostname or IP
  -i ID, --id ID        Site ID — use with delete_website to delete by ID
  --port PORT           SSH port (default: 12345)
  --trust-host          Auto-accept unknown host keys (insecure, trusted networks only)
  --action              See actions below
```

---

## Actions & Examples

### 1. Add a website to the database

```bash
./wp_backup.py --action add_website -u SSH_USERNAME -p 'PASSWORD' -H IP/Hostname -d domain_name -P /home/user/domain_name
```

> Always wrap the password in single quotes to prevent shell expansion.

---

### 2. Delete a website from the database

By domain name:

```bash
./wp_backup.py --action delete_website -d domain_name.com
```

By site ID (use `all_sites` to find the ID):

```bash
./wp_backup.py --action delete_website -i 3
```

---

### 3. List a specific site

```bash
./wp_backup.py --action list_website -d domain_name.com
```

Output:

```
OrderedDict([('wp_id', 3),
             ('domain_name', 'domain_name.com'),
             ('username', 'ssh_user'),
             ('password', 'SOME PASS'),
             ('hostname', '192.168.1.2'),
             ('wp_path', '/home/ssh_user/domain_name.com'),
             ('backup_folder', 'domain_name.com_backup_folder_30-09-2024')])
```

---

### 4. List all sites

```bash
./wp_backup.py --action all_sites
```

Output:

```
(3, 'domain_name.com', 'ssh_user', 'SOME PASS', '192.168.1.2', '/home/ssh_user/domain_name.com', 'domain_name.com_backup_folder_30-09-2024')
```

---

### 5. Backup (credentials from CLI)

```bash
./wp_backup.py --action backup -u SSH_USERNAME -p 'PASSWORD' -d domain_name.com -P /home/user/domain_name.com -H IP/Hostname
```

---

### 6. Restore (credentials from CLI)

```bash
./wp_backup.py --action restore -u SSH_USERNAME -p 'PASSWORD' -d domain_name.com -P /home/user/domain_name.com -H IP/Hostname
```

---

### 7. Backup using stored database credentials

```bash
./wp_backup.py --action backup_db -d domain_name.com
```

---

### 8. Restore using stored database credentials

```bash
./wp_backup.py --action restore_db -d domain_name.com
```

---

### 9. List site details from the database

```bash
./wp_backup.py --action list_website_db -d domain_name.com
```

---

### 10. Check backup folder

Checks whether a backup folder exists on the remote server for today's date.

```bash
./wp_backup.py --action check -u SSH_USERNAME -p 'PASSWORD' -d domain_name.com -P /home/user/domain_name.com -H IP/Hostname
```

---

## Manual Autocomplete Setup

If `make autocomplete` doesn't work for your environment, add this to `~/.bashrc`:

```bash
register-python-argcomplete wp_backup.py >> ~/.bashrc
complete -o nospace -o default -o bashdefault -F _python_argcomplete ./wp_backup.py >> ~/.bashrc
```

> **Important:** Bash completion is tied to the **exact command string** you type.
> The two lines above register completion for both `wp_backup.py` and `./wp_backup.py`.
> If you rename the script, move it to a directory in `$PATH` (e.g. `/usr/local/bin/wp_backup`),
> or call it by its full path (e.g. `/opt/tools/wp_backup.py`), you must update the
> `complete` line to match the new name/path — otherwise tab completion will not trigger.
>
> Example for a script installed as `/usr/local/bin/wp_backup`:
> ```bash
> complete -o nospace -o default -o bashdefault -F _python_argcomplete wp_backup
> ```

Or for global activation (all argcomplete-enabled scripts — handles any name or path automatically):

```bash
sudo activate-global-python-argcomplete
```

### CentOS 7

```bash
curl -o /etc/yum.repos.d/CentOS-Base.repo https://el7.repo.almalinux.org/centos/CentOS-Base.repo
yum -y update
yum -y install python3-paramiko python3-argcomplete
```

Reference: [AlmaLinux ELevate Guide](https://wiki.almalinux.org/elevate/ELevating-CentOS7-to-AlmaLinux-9.html)
