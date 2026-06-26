# CipherVault - Password Manager

**My CS50P Final Project**

CipherVault is a command-line password manager written in Python that lets you generate, store, search, update, and delete credentials securely — all from your terminal. Instead of reusing weak passwords or storing them in plain text, CipherVault helps you create strong, cryptographically secure passwords and organize them in one place.

**Video Demo:** [YouTube Video](https://youtu.be/Tah7sznvaUk)

---

## Features

- **Master Password Protection:** Secured via SHA-256 hashing — the actual password is never stored.
- **Secure Password Generation:** Generate strong passwords using Python's `secrets` module with custom length and symbol options.
- **Password Strength Checker:** Evaluates and scores passwords based on length and character diversity.
- **Add Credentials:** Store a new site, username, and password in the vault.
- **Update Credentials:** Modify an existing credential entry.
- **Search Credentials:** Look up saved credentials by site name or username.
- **List All Credentials:** View all stored credentials in a formatted table.
- **Delete Credentials:** Remove credentials you no longer need.
- **Rich CLI Interface:** Colorful tables and styled messages using the `Rich` library.
- **Fun Exit Message:** A farewell message displayed via `Cowsay` when you quit.

---

## Requirements

- Python 3.7 or later
- Installed libraries:
  - `rich`
  - `cowsay`
  - `pytest`

---

## Setup and Installation

1. Clone the repository:

```bash
git clone https://github.com/me50/Prashast-Srivastava.git
cd CipherVault
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python project.py
```

---

## Detailed Explanation of Code

### `project.py`
This is the main application file containing all core logic.

**`main()`** — Entry point of the program. Handles master password authentication and launches the interactive menu loop where the user chooses operations.

**`create_master_password()`** — Prompts the user to set a master password on first launch. Converts it to a SHA-256 hash using `hashlib` and saves only the hash to `master.hash`. The actual password is never stored.

**`verify_master_password()`** — On each launch, hashes the entered password and compares it to the stored hash. The user gets three attempts before the program exits.

**`generate_password()`** — Generates a cryptographically secure password using Python's `secrets` module. The user can specify a custom length and whether to include symbols. Guarantees at least one character from each selected character set.

**`check_strength()`** — Evaluates a password's strength using a scoring system based on length and character diversity (uppercase, lowercase, digits, symbols). Displays the result to the user.

**`add_credential()`** — Prompts the user for a site name, username, and password (or generates one), then saves the entry to the vault.

**`update_credential()`** — Searches for an existing credential and allows the user to update the username or password.

**`search_credentials()`** — Searches the vault by site name or username and displays matching results in a formatted table.

**`list_credentials()`** — Displays all stored credentials in a Rich-formatted table.

**`delete_credential()`** — Removes a selected credential from the vault after user confirmation.

**`load_vault()` / `save_vault()`** — Handles reading from and writing to `vault.json`, located in the user's home directory.

---

### `test_project.py`
Contains unit tests written with **Pytest**. Tests cover:
- Correctness of the password generator (length, character sets)
- SHA-256 hashing of the master password
- Vault search functionality and edge cases

---

### `requirements.txt`
Lists all external libraries required to run the project:
```
rich
cowsay
pytest
```

---

### `vault.json`
The password vault file where credentials are stored. Located in the user's home directory. Each entry contains the site name, username, password, and a SHA-256 hash of the password.

---

### `master.hash`
Stores only the SHA-256 hash of the master password — never the password itself.

---

### `.gitignore`
Prevents sensitive and generated files from being uploaded to GitHub, including:
- `vault.json`
- `master.hash`
- `__pycache__/`
- Virtual environment folders

---

## How I Came Up With This Project Idea

Passwords are something every developer deals with, and most people handle them badly — reusing weak ones or storing them in plain text. After learning about file handling, hashing, modules, and the `secrets` library during CS50P, I realized I had everything I needed to build something genuinely useful. CipherVault came out of wanting to apply those concepts together into a real-world tool I'd actually use.

---

## Design Choices

**Why `secrets` instead of `random`?**
Python's `random` module is not suitable for security-sensitive tasks. The `secrets` module is specifically designed for generating cryptographically secure random values, making it the right choice for password generation.

**Why SHA-256 for the master password?**
Storing a password in plain text — even locally — is a bad practice. Hashing it with SHA-256 means that even if someone accesses your `master.hash` file, they cannot recover the original password.

**Why not encrypt the vault?**
I considered using `cryptography.fernet` to encrypt stored passwords at rest. For this project, I chose to keep the focus on CS50P concepts: hashing, file handling, JSON storage, modular design, and testing. Fernet-based encryption would be the natural next step in a production version.

**Why Rich?**
Plain terminal output gets hard to read quickly. Rich adds formatted tables and colored messages without much complexity, making the vault much more pleasant to navigate.

---

## Final Note

Building CipherVault was a rewarding experience that brought together almost everything covered in CS50P — functions, dictionaries, file handling, exception handling, modules, unit testing, and third-party libraries — into one cohesive project. It also pushed me to think about *why* certain design decisions matter, not just how to implement them.

---

## Who Am I?

- **Name:** Prashast Srivastava
- **GitHub:** [Prashast-Srivastava](https://github.com/Prashast-Srivastava)
- **edX:** Prashast_71
- **City:** Lucknow
- **Country:** India
