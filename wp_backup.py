#!/usr/bin/env python3
import sys
import argparse
import sqlite3
from datetime import datetime
from collections import OrderedDict
from pprint import pprint

import paramiko
from paramiko import SSHClient
import argcomplete

current_date = datetime.today().strftime("%d-%m-%Y")
exclude_path = "./wp-content/uploads"
DB_PATH = 'wordpress_support.db'


def parse_args():
    parser = argparse.ArgumentParser(
        prog='WordPress Backup Tools',
        description='Back up WordPress sites remotely via SSH'
    )
    parser.add_argument('-u', '--user', help='cPanel username')
    parser.add_argument('-p', '--password', help='cPanel password (use single quotes)')
    parser.add_argument('-d', '--domain', help='Domain name')
    parser.add_argument('-P', '--path', help='WordPress installation path (no trailing slash)')
    parser.add_argument('-H', '--host', help='Hostname or IP')
    parser.add_argument('-i', '--id', type=int, help='Site ID (for delete_website)')
    parser.add_argument('--port', type=int, default=12345, help='SSH port (default: 12345)')
    parser.add_argument('--trust-host', action='store_true',
                        help='Auto-accept unknown host keys (insecure, use only on trusted networks)')
    parser.add_argument('--action', choices=[
        'backup', 'restore', 'add_website', 'delete_website',
        'list_website', 'all_sites', 'check',
        'backup_db', 'restore_db', 'list_website_db',
    ], default='check')
    argcomplete.autocomplete(parser)
    return parser.parse_args()


def make_ssh_client(hostname, port, username, password, trust_host=False):
    client = SSHClient()
    client.load_system_host_keys()
    if trust_host:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    else:
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(hostname, port, username, password)
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


class WpDatabase:
    def __init__(self, db_path=DB_PATH):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._init_table()

    def _init_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS wordpress_sites (
                wp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain_name TEXT UNIQUE,
                username TEXT,
                password TEXT,
                hostname TEXT,
                wp_path TEXT,
                backup_folder TEXT
            )
        """)
        self.connection.commit()

    def add_website(self, domain_name, username, password, hostname, wp_path, backup_folder):
        self.cursor.execute(
            "INSERT INTO wordpress_sites (domain_name, username, password, hostname, wp_path, backup_folder) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (domain_name, username, password, hostname, wp_path, backup_folder)
        )
        self.connection.commit()

    def delete_website(self, domain_name=None, site_id=None):
        if site_id is not None:
            self.cursor.execute("DELETE FROM wordpress_sites WHERE wp_id = ?", (site_id,))
        elif domain_name is not None:
            self.cursor.execute("DELETE FROM wordpress_sites WHERE domain_name = ?", (domain_name,))
        else:
            raise ValueError("delete_website requires domain_name or site_id")
        self.connection.commit()
        return self.cursor.rowcount

    def get_site(self, domain_name):
        self.cursor.execute(
            "SELECT * FROM wordpress_sites WHERE domain_name = ?",
            (domain_name,)
        )
        return self.cursor.fetchone()

    def list_all(self):
        self.cursor.execute("SELECT * FROM wordpress_sites")
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()


class WordPressBackup:
    def __init__(self, username, password, hostname, port, wordpress_path, domain_name, trust_host=False):
        self.username = username
        self.password = password
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
                self.hostname, self.port, self.username, self.password, self.trust_host
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


def usage():
    print("#" * 50)
    print()
    print("EXAMPLE: Add a website to the database")
    print()
    print("  ./wp_backup.py --action add_website -u USER -d DOMAIN"
          " -P /path/to/wp -p 'PASSWORD' -H HOST")
    print()
    print("Actions that read from the database (use -d DOMAIN to select site):")
    print("  backup_db, restore_db, list_website_db")
    print()
    print("Actions that use CLI credentials (-u -p -H -P -d):")
    print("  backup, restore, check")
    print()
    print("#" * 50)


def _require_args(args, *fields):
    missing = [f for f in fields if not getattr(args, f, None)]
    if missing:
        print(f"Error: missing required arguments: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def main():
    args = parse_args()
    db = WpDatabase()

    try:
        if args.action == 'add_website':
            _require_args(args, 'user', 'domain', 'path', 'password', 'host')
            backup_folder = f'{args.domain}_backup_folder_{current_date}'
            db.add_website(args.domain, args.user, args.password, args.host, args.path, backup_folder)
            print(f"Website {args.domain} added successfully.")
            print("Run with --action list_website -d DOMAIN to verify.")

        elif args.action == 'delete_website':
            if not args.id and not args.domain:
                print("Error: delete_website requires -d DOMAIN or -i ID", file=sys.stderr)
                sys.exit(1)
            deleted = db.delete_website(domain_name=args.domain, site_id=args.id)
            if deleted:
                label = f"ID {args.id}" if args.id else args.domain
                print(f"Website {label} deleted.")
            else:
                label = f"ID {args.id}" if args.id else args.domain
                print(f"No site found for {label}.")

        elif args.action == 'list_website':
            _require_args(args, 'domain')
            row = db.get_site(args.domain)
            if not row:
                print(f"No site found for domain: {args.domain}")
            else:
                cols = ['wp_id', 'domain_name', 'username', 'password', 'hostname', 'wp_path', 'backup_folder']
                pprint(OrderedDict(zip(cols, row)))

        elif args.action == 'all_sites':
            for site in db.list_all():
                print(site)

        elif args.action in ('backup', 'restore', 'check'):
            _require_args(args, 'user', 'domain', 'path', 'password', 'host')
            wp = WordPressBackup(
                args.user, args.password, args.host, args.port,
                args.path, args.domain, args.trust_host
            )
            try:
                if args.action == 'backup':
                    wp.create_backup()
                elif args.action == 'restore':
                    wp.restore_backup()
                else:
                    wp.check_backup_folder()
            finally:
                wp.close()

        elif args.action in ('backup_db', 'restore_db', 'list_website_db'):
            _require_args(args, 'domain')
            row = db.get_site(args.domain)
            if not row:
                print(f"No site found for domain: {args.domain}")
                sys.exit(1)
            _, domain_name, username, password, hostname, wp_path, _ = row

            if args.action == 'list_website_db':
                print(f"Domain:   {domain_name}")
                print(f"Username: {username}")
                print(f"Host:     {hostname}")
                print(f"WP Path:  {wp_path}")
            else:
                wp = WordPressBackup(
                    username, password, hostname, args.port, wp_path, domain_name, args.trust_host
                )
                try:
                    if args.action == 'backup_db':
                        wp.create_backup()
                    else:
                        wp.restore_backup()
                finally:
                    wp.close()

        else:
            usage()

    finally:
        db.close()


if __name__ == "__main__":
    main()
