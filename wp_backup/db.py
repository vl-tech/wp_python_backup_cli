import sqlite3

from .crypto import encrypt, decrypt, is_encrypted

DB_PATH = 'wordpress_support.db'


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
                port INTEGER DEFAULT 12345,
                ssh_key TEXT
            )
        """)
        self.connection.commit()
        self._migrate()

    def _migrate(self):
        cols = [row[1] for row in self.cursor.execute("PRAGMA table_info(wordpress_sites)")]
        if 'port' not in cols:
            self.cursor.execute("ALTER TABLE wordpress_sites ADD COLUMN port INTEGER DEFAULT 12345")
            self.connection.commit()
        if 'backup_folder' in cols:
            self.cursor.execute("ALTER TABLE wordpress_sites DROP COLUMN backup_folder")
            self.connection.commit()
        if 'ssh_key' not in cols:
            self.cursor.execute("ALTER TABLE wordpress_sites ADD COLUMN ssh_key TEXT")
            self.connection.commit()
        self._migrate_encrypt_passwords()

    def _migrate_encrypt_passwords(self):
        rows = self.cursor.execute("SELECT wp_id, password FROM wordpress_sites").fetchall()
        for wp_id, password in rows:
            if password and not is_encrypted(password):
                self.cursor.execute(
                    "UPDATE wordpress_sites SET password = ? WHERE wp_id = ?",
                    (encrypt(password), wp_id)
                )
        self.connection.commit()

    def add_website(self, domain_name, username, hostname, port, wp_path,
                    password=None, ssh_key=None):
        self.cursor.execute(
            "INSERT INTO wordpress_sites "
            "(domain_name, username, password, hostname, wp_path, port, ssh_key) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (domain_name, username, encrypt(password) if password else None,
             hostname, wp_path, port, ssh_key)
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

    def _decrypt_row(self, row):
        if row is None:
            return None
        wp_id, domain_name, username, password, hostname, wp_path, port, ssh_key = row
        return (wp_id, domain_name, username, decrypt(password) if password else None,
                hostname, wp_path, port, ssh_key)

    def get_site(self, domain_name):
        self.cursor.execute(
            "SELECT * FROM wordpress_sites WHERE domain_name = ?",
            (domain_name,)
        )
        return self._decrypt_row(self.cursor.fetchone())

    def list_all(self):
        self.cursor.execute("SELECT * FROM wordpress_sites")
        return [self._decrypt_row(row) for row in self.cursor.fetchall()]

    def close(self):
        self.connection.close()
