# wp_backup.py — Updates & Fixes

## Changes Made

### 1. SQL Injection Fix (Security)
**Before:** SQL queries were built with f-strings, allowing injected SQL via any user-controlled field (domain, username, etc.).
**After:** All queries use SQLite parameterized statements (`?` placeholders). `WpDatabase` now owns its connection and cursor internally.

### 2. SSH Host Key Verification (Security)
**Before:** Every connection used `AutoAddPolicy()`, silently accepting any host key — vulnerable to man-in-the-middle attacks.
**After:** `make_ssh_client()` loads system known_hosts and uses `RejectPolicy()` by default. Pass `--trust-host` to opt into the old behavior on trusted networks.

### 3. Hardcoded SSH Port
**Before:** Port was a global variable `port = 12345` with no way to change it from the CLI.
**After:** Added `--port` argument (default: `12345`) so any SSH port can be used without editing the file.

### 4. Duplicate `BackupFromDatabase` Class Removed
**Before:** `BackupFromDatabase` was a near-identical copy of `WordPressBackup` — same methods, same logic, duplicated in full.
**After:** Merged into a single `WordPressBackup` class that accepts credentials as constructor parameters. `backup_db` and `restore_db` actions instantiate it with data pulled from the database.

### 5. SSH Reconnects on Every Method Call
**Before:** `create_backup()`, `restore_backup()`, and `check_backup_folder()` each created a brand-new `SSHClient` connection. `connect_to_host()` existed but was never used.
**After:** `WordPressBackup._connect()` connects once and reuses the active transport. `close()` cleanly shuts it down at the end.

### 6. `time.sleep()` Replaced with Proper Wait
**Before:** `time.sleep(2)` was used after SSH commands, assuming they'd finish in 2 seconds.
**After:** `run_command()` calls `stdout.channel.recv_exit_status()` to block until the remote command actually completes, then checks and returns the exit code.

### 7. `usage_function()` Running at Import Time
**Before:** `usage_function()` was called at module level (line 28), printing the usage banner on every invocation regardless of the action.
**After:** `usage()` is only called inside `main()` when no recognized action is matched.

### 8. Tar Command Bug Fixed
**Before:** Missing space in the tar command: `--exclude='{exclude_path}'-czf` — the flag was glued to `-czf`, breaking the archive silently.
**After:** Correct spacing: `--exclude='{exclude_path}' --exclude-backups -czf`.

### 9. Duplicate `pprint` Import Removed
**Before:** `pprint` was imported twice (lines 8 and 11). `time` was imported but only used for `sleep` calls (now removed).
**After:** Single import of each module; `time` removed entirely.

### 10. Action Names Renamed (`backup2` → `backup_db`, etc.)
**Before:** `backup2`, `restore2`, `list_website2` — unclear naming.
**After:** `backup_db`, `restore_db`, `list_website_db` — names reflect that credentials come from the database.

### 11. `sys.exit()` Inside Return Statement Removed
**Before:** `return {...}, sys.exit('End of Program! Bye Bye')` — calling `sys.exit()` as part of a return tuple is confusing and terminates inside a method.
**After:** Methods return normally; `main()` exits cleanly after the action completes.

### 12. `WpDatabase` Now Creates Table if Missing
**Before:** The table had to exist before running any action — no `CREATE TABLE` anywhere in the code.
**After:** `WpDatabase._init_table()` runs `CREATE TABLE IF NOT EXISTS` on startup.

### 13. Missing Argument Validation
**Before:** No check that required flags (`-u`, `-p`, `-H`, `-P`, `-d`) were provided for actions that need them — would crash with an unhelpful `AttributeError`.
**After:** `_require_args()` validates required fields per action and exits with a clear error message.
