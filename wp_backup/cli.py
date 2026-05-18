import sys
import argparse
from collections import OrderedDict
from pprint import pprint

import argcomplete

from .db import WpDatabase
from .ssh import WordPressBackup


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
    parser.add_argument('-k', '--key', help='Path to SSH private key file')
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


def _require_args(args, *fields):
    missing = [f for f in fields if not getattr(args, f, None)]
    if missing:
        print(f"Error: missing required arguments: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


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


def main():
    args = parse_args()
    db = WpDatabase()

    try:
        if args.action == 'add_website':
            _require_args(args, 'user', 'domain', 'path', 'host')
            if not args.password and not args.key:
                print("Error: add_website requires -p PASSWORD or -k KEY_FILE (or both)", file=sys.stderr)
                sys.exit(1)
            db.add_website(args.domain, args.user, args.host, args.port, args.path,
                           password=args.password, ssh_key=args.key)
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
                cols = ['wp_id', 'domain_name', 'username', 'password', 'hostname', 'wp_path', 'port', 'ssh_key']
                pprint(OrderedDict(zip(cols, row)))

        elif args.action == 'all_sites':
            cols = ['wp_id', 'domain_name', 'username', 'password', 'hostname', 'wp_path', 'port', 'ssh_key']
            for site in db.list_all():
                pprint(OrderedDict(zip(cols, site)))
                print()

        elif args.action in ('backup', 'restore', 'check'):
            _require_args(args, 'user', 'domain', 'path', 'host')
            if not args.password and not args.key:
                print("Error: backup/restore/check requires -p PASSWORD or -k KEY_FILE", file=sys.stderr)
                sys.exit(1)
            wp = WordPressBackup(
                args.user, args.host, args.port, args.path, args.domain,
                password=args.password, key_file=args.key, trust_host=args.trust_host
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
            _, domain_name, username, password, hostname, wp_path, port, ssh_key = row

            if args.action == 'list_website_db':
                print(f"Domain:   {domain_name}")
                print(f"Username: {username}")
                print(f"Host:     {hostname}")
                print(f"Port:     {port}")
                print(f"WP Path:  {wp_path}")
                print(f"SSH Key:  {ssh_key or '(password auth)'}")
            else:
                wp = WordPressBackup(
                    username, hostname, port, wp_path, domain_name,
                    password=password, key_file=ssh_key, trust_host=args.trust_host
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
