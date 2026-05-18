import sys
from datetime import datetime

import paramiko
from paramiko import SSHClient

current_date = datetime.today().strftime("%d-%m-%Y")
exclude_path = "./wp-content/uploads"


def make_ssh_client(hostname, port, username, password=None, trust_host=False, key_file=None):
    client = SSHClient()
    client.load_system_host_keys()
    if trust_host:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    else:
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(hostname, port, username, password=password, key_filename=key_file)
    return client


def run_command(client, command, description=None):
    if description:
        print(f"  -> {description}")
    _, stdout, stderr = client.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8').strip()
    err = stderr.read().decode('utf-8').strip()
    if out:
        print(out)
    if err:
        print(f"[stderr] {err}", file=sys.stderr)
    return exit_code, out, err


class WordPressBackup:
    def __init__(self, username, hostname, port, wordpress_path, domain_name,
                 password=None, key_file=None, trust_host=False):
        self.username = username
        self.password = password
        self.key_file = key_file
        self.hostname = hostname
        self.port = port
        self.wordpress_path = wordpress_path
        self.domain_name = domain_name
        self.trust_host = trust_host
        self.backup_folder = f'{domain_name}_backup_folder_{current_date}'
        self.backup_tar_file = f"{self.backup_folder}/{domain_name}-backup-{current_date}.tar.gz"
        self.database_backup_file = f"{self.backup_folder}/{domain_name}-backup-{current_date}.sql"
        self._client = None

    def _connect(self):
        transport = self._client.get_transport() if self._client else None
        if transport is None or not transport.is_active():
            self._client = make_ssh_client(
                self.hostname, self.port, self.username,
                password=self.password, trust_host=self.trust_host, key_file=self.key_file
            )
            print(f"Connected to {self.hostname}")
        return self._client

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def check_backup_folder(self):
        client = self._connect()
        exit_code, output, _ = run_command(client, f'ls {self.backup_folder}')
        if exit_code != 0:
            run_command(client, f'mkdir -p {self.backup_folder}', 'Creating backup folder')
            print(f"Backup folder created: {self.backup_folder}")
        else:
            print(f"Backup folder already exists: {self.backup_folder}")
            if output:
                print(output)

    def create_backup(self):
        client = self._connect()
        run_command(client, f'mkdir -p {self.backup_folder}', 'Creating backup folder')

        print("Starting database and files backup...")
        cmd = (
            f"wp --path={self.wordpress_path} db export {self.database_backup_file} && "
            f"tar --exclude='{exclude_path}' --exclude-backups -czf {self.backup_tar_file} "
            f"-C {self.wordpress_path} ."
        )
        exit_code, _, _ = run_command(client, cmd, 'Exporting database and archiving files')
        if exit_code != 0:
            print("Backup failed. Check stderr above.", file=sys.stderr)
            return

        print("Backup complete. Listing backup folder:")
        run_command(client, f'ls -al {self.backup_folder}')

    def restore_backup(self):
        client = self._connect()

        print(f"Deleting WP root files from {self.wordpress_path} (keeping wp-content)")
        run_command(
            client,
            f"find {self.wordpress_path} -mindepth 1 -maxdepth 1 ! -name 'wp-content' -delete",
            'Removing WP root files'
        )

        print("Deleting wp-content files (keeping uploads)")
        run_command(
            client,
            f"find {self.wordpress_path}/wp-content -mindepth 1 -maxdepth 1 ! -name 'uploads' -delete",
            'Removing wp-content (keeping uploads)'
        )

        print(f"Extracting {self.backup_tar_file} to {self.wordpress_path}")
        exit_code, _, _ = run_command(
            client, f'tar -xzf {self.backup_tar_file} -C {self.wordpress_path}', 'Extracting archive'
        )
        if exit_code != 0:
            print("File restore failed. Check stderr above.", file=sys.stderr)
            return

        print("Files restored. Importing database...")
        exit_code, _, _ = run_command(
            client,
            f'wp --path={self.wordpress_path} db import {self.database_backup_file}',
            'Importing database'
        )
        if exit_code != 0:
            print("Database import failed. Check stderr above.", file=sys.stderr)
            return

        print("Restore completed successfully.")
