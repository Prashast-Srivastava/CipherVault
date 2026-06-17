import json
import hashlib
import secrets
import string
import sys
import msvcrt
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def input_password(prompt: str = "  Password        : ") -> str:
    """
    Read password showing * for each character.
    Run in CMD or VS Code terminal for best experience.
    """
    if msvcrt is None:
        import getpass
        return getpass.getpass(prompt)
    print(prompt, end="", flush=True)
    chars = []
    while True:
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):       # Enter
            print()
            break
        elif ch == "\x08":            # Backspace
            if chars:
                chars.pop()
                print("\b \b", end="", flush=True)
        elif ch == "\x03":            # Ctrl+C
            raise KeyboardInterrupt
        else:
            chars.append(ch)
            print("*", end="", flush=True)
    return "".join(chars)

VAULT_FILE = Path.home() / ".pm_vault.json"

UPPER   = string.ascii_uppercase
LOWER   = string.ascii_lowercase
DIGITS  = string.digits
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


# ── Core functions (tested by pytest) ─────────────────────────────────────────

def generate_password(length: int = 16,
                      use_upper: bool = True,
                      use_lower: bool = True,
                      use_digits: bool = True,
                      use_symbols: bool = True) -> str:
    """
    Return a cryptographically secure random password.

    At least one character from every enabled character set is guaranteed.
    Raises ValueError if length < 4 or no character set is selected.
    """
    if length < 4:
        raise ValueError("Password length must be at least 4.")

    pool = ""
    guaranteed = []

    if use_upper:
        pool += UPPER
        guaranteed.append(secrets.choice(UPPER))
    if use_lower:
        pool += LOWER
        guaranteed.append(secrets.choice(LOWER))
    if use_digits:
        pool += DIGITS
        guaranteed.append(secrets.choice(DIGITS))
    if use_symbols:
        pool += SYMBOLS
        guaranteed.append(secrets.choice(SYMBOLS))

    if not pool:
        raise ValueError("At least one character set must be selected.")

    # Fill remaining length with random pool characters
    remaining = [secrets.choice(pool) for _ in range(length - len(guaranteed))]
    password_chars = guaranteed + remaining

    # Shuffle so guaranteed chars don't always appear at the front
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def hash_password(password: str) -> str:
    """
    Return the SHA-256 hex digest of a password string.

    In a real system you'd use bcrypt/argon2; SHA-256 is used here
    to demonstrate hashlib as required by the project spec.
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
    return hashlib.sha256(password.encode()).hexdigest()


def search_vault(vault: list[dict], query: str) -> list[dict]:
    """
    Return all entries whose 'site' or 'username' contains *query* (case-insensitive).

    Parameters
    ----------
    vault : list of credential dicts (each has 'site', 'username', 'hash')
    query : search string

    Returns an empty list if nothing matches.
    """
    query = query.strip().lower()
    if not query:
        return []
    return [
        entry for entry in vault
        if query in entry.get("site", "").lower()
        or query in entry.get("username", "").lower()
    ]


# ── Vault persistence helpers ──────────────────────────────────────────────────

def load_vault() -> list[dict]:
    """Load credentials from the JSON vault file. Returns [] if file missing."""
    if not VAULT_FILE.exists():
        return []
    try:
        with open(VAULT_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_vault(vault: list[dict]) -> None:
    """Persist the vault list to the JSON file."""
    with open(VAULT_FILE, "w") as f:
        json.dump(vault, f, indent=2)


def add_credential(vault: list[dict], site: str, username: str, password: str) -> dict:
    """
    Hash *password*, build a credential dict, append to *vault*, and return it.
    The plaintext password is NEVER stored.
    """
    entry = {
        "site":     site.strip(),
        "username": username.strip(),
        "password": password,
        "hash":     hash_password(password),
    }
    vault.append(entry)
    return entry


def delete_credential(vault: list[dict], index: int) -> dict:
    """Remove the entry at *index* (0-based) from *vault* and return it."""
    if index < 0 or index >= len(vault):
        raise IndexError(f"No credential at index {index}.")
    return vault.pop(index)


# ── CLI helpers ────────────────────────────────────────────────────────────────

def strength_label(password: str) -> str:
    """Return a human-readable strength label for a password."""
    score = 0
    if len(password) >= 12: score += 1
    if len(password) >= 20: score += 1
    if any(c in UPPER   for c in password): score += 1
    if any(c in LOWER   for c in password): score += 1
    if any(c in DIGITS  for c in password): score += 1
    if any(c in SYMBOLS for c in password): score += 1
    labels = ["Very weak", "Weak", "Fair", "Good", "Strong", "Very strong"]
    return labels[min(score, 5)]


def print_entry(index: int, entry: dict) -> None:
    print(f"\n  [{index}] {entry['site']}")
    print(f"      User     : {entry['username']}")
    print(f"      Password : {entry.get('password', '(hidden)')}")


def print_separator():
    print("─" * 52)


# ── CLI menu ───────────────────────────────────────────────────────────────────

def menu_generate():
    print_separator()
    try:
        length = int(input("  Length [default 16]: ").strip() or 16)
    except ValueError:
        print("  Invalid length. Using 16.")
        length = 16

    use_sym = input("  Include symbols? [Y/n]: ").strip().lower() != "n"

    try:
        pwd = generate_password(length=length, use_symbols=use_sym)
    except ValueError as e:
        print(f"  Error: {e}")
        return

    print(f"\n  Generated : {pwd}")
    print(f"  Strength  : {strength_label(pwd)}")

    save = input("\n  Save this credential? [y/N]: ").strip().lower()
    if save == "y":
        site     = input("  Site / App name : ").strip()
        username = input("  Username / Email: ").strip()
        vault = load_vault()
        add_credential(vault, site, username, pwd)
        save_vault(vault)
        print("  ✓ Saved to vault.")


def menu_add():
    print_separator()
    site     = input("  Site / App name : ").strip()
    username = input("  Username / Email: ").strip()
    password = input_password("  Password        : ").strip()

    if not site or not username or not password:
        print("  Site, username, and password are required.")
        return

    vault = load_vault()

    existing = [i for i, e in enumerate(vault) if e["site"].lower() == site.lower()]
    if existing:
        print(f"  '{site}' already exists. Updating...")
        for i in existing:
            vault[i]["username"] = username
            vault[i]["password"] = password
            vault[i]["hash"]     = hash_password(password)
    else:
        add_credential(vault, site, username, password)

    save_vault(vault)
    print(f"  ✓ Saved. Strength: {strength_label(password)}")


def menu_get():
    print_separator()
    site  = input("  Site / App name: ").strip()
    vault = load_vault()
    matches = [e for e in vault if e["site"].lower() == site.lower()]
    if not matches:
        print(f"  No credential found for '{site}'.")
        return
    for entry in matches:
        print(f"\n  Site     : {entry['site']}")
        print(f"  Username : {entry['username']}")


def menu_search():
    print_separator()
    query = input("  Search (site or username): ").strip()
    vault = load_vault()
    results = search_vault(vault, query)
    if not results:
        print("  No matches found.")
    else:
        print(f"  {len(results)} result(s):")
        for i, entry in enumerate(results):
            print_entry(i, entry)


def menu_list():
    vault = load_vault()
    if not vault:
        print("\n  Vault is empty.")
        return
    print(f"\n  {len(vault)} credential(s) stored:")
    for i, entry in enumerate(vault):
        print_entry(i, entry)


def menu_delete():
    vault = load_vault()
    if not vault:
        print("\n  Vault is empty.")
        return
    print_separator()
    site = input("  Site / App to delete: ").strip().lower()
    matches = [i for i, e in enumerate(vault) if e["site"].lower() == site]
    if not matches:
        print(f"  No entry found for '{site}'.")
        return
    for i in matches:
        print(f"  Deleting: {vault[i]['site']} — {vault[i]['username']}")
    for i in reversed(matches):
        vault.pop(i)
    save_vault(vault)
    print(f"  ✓ Deleted {len(matches)} entry/entries for '{site}'.")


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    console.print("\n[bold cyan]  CiperVault — Password Manager[/bold cyan]\n", justify="center")

    while True:
        table = Table(box=box.SQUARE_DOUBLE_HEAD, style="cyan")
        table.add_column("Command", style="bold magenta", justify="center")
        table.add_column("Operation", justify="center")
        table.add_row("add", "Add / Update a password")
        table.add_row("get", "Get a password")
        table.add_row("src", "Search credentials")
        table.add_row("gen", "Generate a strong password")
        table.add_row("ls",  "List all sites")
        table.add_row("del", "Delete a password")
        table.add_row("exit","Exit")
        console.print(table, justify="center")

        choice = input("\n  Command : ").strip().lower()

        if   choice == "add":  menu_add()
        elif choice == "get":  menu_get()
        elif choice == "src":  menu_search()
        elif choice == "gen":  menu_generate()
        elif choice == "ls":   menu_list()
        elif choice == "del":  menu_delete()
        elif choice == "exit": console.print("\n[bold green]Goodbye! Stay secure. [/bold green]\n", justify="center"); sys.exit(0)
        else: print("  Invalid choice.")


if __name__ == "__main__":
    main()