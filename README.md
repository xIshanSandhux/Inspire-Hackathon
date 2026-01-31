# 🔐 Fingerprint Identity Blockchain System

A secure Python application that stores fingerprint and ID associations on a blockchain, ensuring data integrity, immutability, and secure access control.

## 🌟 Features

- **Fingerprint Hash Input** - Accept fingerprint hash from biometric devices
- **Encrypted ID Storage** - IDs are encrypted using the fingerprint hash as the key
- **Structured ID Data** - Support for PASSPORT and BCID with metadata
- **Secure Access Control** - Only fingerprint owner can decrypt their data
- **Blockchain Storage** - All records stored on a tamper-proof blockchain
- **Data Persistence** - SQLite database for reliable storage
- **Chain Verification** - Verify blockchain integrity at any time
- **Docker Support** - Run in containers for easy deployment
- **Interactive CLI** - User-friendly command-line interface

## 📁 Project Structure

```
├── blockchain.py      # Blockchain implementation with mining & cryptography
├── database.py        # SQLite database for persistence
├── encryption.py      # AES-256 encryption for ID data
├── main.py            # Main application with CLI
├── Dockerfile         # Docker container setup
├── docker-compose.yml # Docker Compose configuration
├── Makefile           # Build and run commands
├── requirements.txt   # Python dependencies
└── README.md          # This documentation
```

---

## 📚 Blockchain 101: A Beginner's Guide

### What is a Blockchain?

Think of a blockchain as a **digital notebook that cannot be erased**. Once you write something, it's permanent.

```
Traditional Database:              Blockchain:
┌─────────────┐                   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Record 1   │  ← Can edit       │ Block 1 │──▶│ Block 2 │──▶│ Block 3 │
│  Record 2   │  ← Can delete     └─────────┘   └─────────┘   └─────────┘
│  Record 3   │                      ↑              ↑              ↑
└─────────────┘                   PERMANENT     PERMANENT      PERMANENT
                                  (cannot change any of these)
```

### The Key Concepts

#### 1. Blocks
A block is like a page in that notebook. It contains:
- **Data** (the information you want to store)
- **Hash** (a unique fingerprint of this block)
- **Previous Hash** (link to the previous block)

#### 2. Chain
Blocks are linked together through hashes. Each block contains the hash of the previous block, creating a chain.

```
Block 1                  Block 2                  Block 3
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│ Data: "Hello"  │       │ Data: "World"  │       │ Data: "!"      │
│ Hash: ABC123   │◄──────│ Prev: ABC123   │◄──────│ Prev: DEF456   │
│ Prev: 000000   │       │ Hash: DEF456   │       │ Hash: GHI789   │
└────────────────┘       └────────────────┘       └────────────────┘
```

#### 3. Hash = Digital Fingerprint
A hash is a fixed-length string generated from data. The same data always produces the same hash:

```
Input: "Hello"     → Hash: 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
Input: "Hello!"    → Hash: 3617a3e7d7d0e0f0e8e9b7e1a2c3d4f5e6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1
                          ↑ Completely different! (even one character change)
```

#### 4. Immutability (Why You Can't Cheat)

If someone tries to change Block 2:

```
BEFORE TAMPERING:
Block 1 (Hash: ABC) ──▶ Block 2 (Prev: ABC, Hash: DEF) ──▶ Block 3 (Prev: DEF)
                                    ✓ Valid chain

AFTER TAMPERING Block 2:
Block 1 (Hash: ABC) ──▶ Block 2 (Prev: ABC, Hash: XYZ) ──▶ Block 3 (Prev: DEF)
                                              ↑                        ↑
                                        Changed!              Still expects DEF!
                                              ✗ INVALID - Chain broken!
```

To successfully tamper, you'd need to re-compute **every block after it** - which is computationally expensive due to mining.

### Real-World Blockchain Example: Bitcoin

The most famous blockchain is **Bitcoin**. Here's how it compares:

| Aspect | Bitcoin | This Project |
|--------|---------|--------------|
| **Purpose** | Digital currency transactions | Fingerprint-ID associations |
| **Data stored** | "Alice sent 1 BTC to Bob" | "Fingerprint X has IDs Y, Z" |
| **Mining difficulty** | Very high (10 min/block) | Low (instant, difficulty=2) |
| **Network** | Thousands of computers worldwide | Single computer (local) |
| **Consensus** | Proof of Work (global agreement) | None needed (single user) |

```
BITCOIN TRANSACTION BLOCK:
┌─────────────────────────────────────────┐
│ Block #750,000                          │
├─────────────────────────────────────────┤
│ Transactions:                           │
│   • Alice → Bob: 0.5 BTC                │
│   • Charlie → Dave: 1.2 BTC             │
│   • Eve → Frank: 0.001 BTC              │
│   ... (thousands more)                  │
├─────────────────────────────────────────┤
│ Previous Hash: 00000000000000000003...  │
│ This Hash:     00000000000000000001...  │
│ Nonce: 2,891,034,827                    │
└─────────────────────────────────────────┘

THIS PROJECT'S BLOCK:
┌─────────────────────────────────────────┐
│ Block #5                                │
├─────────────────────────────────────────┤
│ Data:                                   │
│   • Fingerprint: a1b2c3d4e5f6...        │
│   • IDs: [PASSPORT, BCID] (encrypted)   │
├─────────────────────────────────────────┤
│ Previous Hash: 00a7b8c9d0e1f2...        │
│ This Hash:     00f1e2d3c4b5a6...        │
│ Nonce: 847                              │
└─────────────────────────────────────────┘
```

---

## ❓ FAQ: Common Questions

### Can I Update or Add New IDs to the Same Fingerprint?

**Short answer: No, you cannot modify existing records.**

**Long answer:** This is by design! Blockchain is **append-only**. Here's what happens:

```
Scenario: User registered PASSPORT, now wants to add BCID

WHAT YOU MIGHT EXPECT:
Block 5: { fingerprint: "abc", ids: ["PASSPORT"] }
         ↓ (modify)
Block 5: { fingerprint: "abc", ids: ["PASSPORT", "BCID"] }  ← IMPOSSIBLE!

WHAT ACTUALLY HAPPENS:
Block 5: { fingerprint: "abc", ids: ["PASSPORT"] }          ← Original (unchanged)
         ↓ (new block)
Block 6: { fingerprint: "abc", ids: ["PASSPORT", "BCID"] }  ← New complete record
```

**Options for your use case:**

| Approach | How It Works | Pros | Cons |
|----------|--------------|------|------|
| **Add new block** | Create a new record with all IDs | Keeps history | Multiple records per fingerprint |
| **Application logic** | App returns latest record only | Simple for users | Older blocks still exist |
| **Don't use blockchain** | Use regular database | Supports updates | Loses immutability benefits |

**To add IDs in this system:** Register the fingerprint again with ALL IDs (old + new). The search will find all records.

### When Does a Blockchain Break?

A blockchain can become invalid or compromised in these situations:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BLOCKCHAIN FAILURE MODES                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. DATA CORRUPTION                                                 │
│     ┌─────────┐     ┌─────────┐     ┌─────────┐                    │
│     │ Block 1 │────▶│ Block 2 │──X──│ Block 3 │                    │
│     └─────────┘     └─────────┘     └─────────┘                    │
│                          ↑                                          │
│                     File corrupted / disk failure                   │
│     Result: Chain validation fails, data after corruption lost      │
│                                                                     │
│  2. TAMPERING DETECTED                                              │
│     Someone edits block data directly in database                   │
│     Result: verify_chain() returns False, trust is broken           │
│                                                                     │
│  3. 51% ATTACK (distributed blockchains only)                       │
│     Attacker controls majority of network computing power           │
│     Result: Can rewrite history (NOT applicable to this project)    │
│                                                                     │
│  4. KEY LOSS                                                        │
│     User forgets their fingerprint hash                             │
│     Result: Encrypted IDs cannot be decrypted (data locked forever) │
│                                                                     │
│  5. GENESIS BLOCK DELETED                                           │
│     First block in chain is removed                                 │
│     Result: Entire chain becomes invalid                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Is Blockchain Even Needed Here? (Honest Assessment)

**The honest answer: It depends on your requirements.**

#### ✅ When Blockchain Makes Sense

| Requirement | Why Blockchain Helps |
|-------------|---------------------|
| **Audit trail** | Every record is timestamped and permanent |
| **Tamper detection** | Any modification is immediately detectable |
| **Regulatory compliance** | Prove data hasn't been altered |
| **Distrust of admins** | Even database admins can't secretly modify records |
| **Historical proof** | Prove what data existed at a specific time |

#### ❌ When a Regular Database is Better

| Requirement | Why Database is Better |
|-------------|----------------------|
| **Updates needed** | Databases support UPDATE, blockchain doesn't |
| **Delete functionality** | GDPR "right to be forgotten" = impossible with blockchain |
| **Performance** | Databases are faster (no mining overhead) |
| **Storage efficiency** | Blockchain duplicates data across blocks |
| **Simple CRUD app** | Blockchain adds unnecessary complexity |

#### 🤔 For This Specific Project

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HONEST ASSESSMENT                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  BLOCKCHAIN BENEFITS HERE:                                          │
│  ✓ Tamper-proof audit trail of ID registrations                    │
│  ✓ Can prove when an ID was registered                              │
│  ✓ Cannot secretly delete or modify records                         │
│  ✓ Good for learning blockchain concepts!                           │
│                                                                     │
│  POTENTIAL OVERKILL:                                                │
│  • Single-user system doesn't need distributed consensus            │
│  • Mining adds overhead for little benefit locally                  │
│  • A signed database log could achieve similar goals                │
│  • No network = no decentralization benefit                         │
│                                                                     │
│  VERDICT:                                                           │
│  For a PRODUCTION system: Consider simpler alternatives             │
│  For LEARNING/DEMO: Blockchain is great for understanding concepts  │
│  For AUDIT REQUIREMENTS: Blockchain provides strong guarantees      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Alternative Approaches

If you decide blockchain is overkill, here are alternatives:

```python
# Alternative 1: Signed Database Records
record = {
    "data": {"fingerprint": "abc", "ids": ["PASSPORT"]},
    "timestamp": 1706640000,
    "signature": sign(data + timestamp, private_key)  # Proves integrity
}

# Alternative 2: Append-Only Log with Hashes
log_entry = {
    "data": {...},
    "hash": sha256(data + previous_entry_hash)  # Chain without mining
}

# Alternative 3: Just a Regular Database
# Simple, fast, supports updates and deletes
# Use database triggers for audit logging
```

---

## 🆔 ID Data Structure

IDs are stored as structured JSON with PASSPORT and BCID as the only valid types:

```json
{
  "PASSPORT": {
    "id": "123456789",
    "metadata": {
      "country": "Canada",
      "expiry_date": "2030-12-31"
    }
  },
  "BCID": {
    "id": "987654321",
    "metadata": {
      "issued_by": "BC Services Card",
      "issue_date": "2020-01-01"
    }
  }
}
```

### ID Structure Rules

| Field | Required | Description |
|-------|----------|-------------|
| `PASSPORT` / `BCID` | At least one | Valid ID types (keys) |
| `id` | ✅ Yes | The actual ID number (required) |
| `metadata` | ❌ No | Optional key-value pairs for additional info |

### Encryption

- **All ID data is encrypted** using AES-256 (or XOR fallback)
- **Fingerprint hash is the encryption key** - only the owner can decrypt
- **Stored encrypted on blockchain** - even admins cannot read the IDs
- **Decryption only happens** when user provides correct fingerprint hash

---

## 🔒 Security Architecture

### How the Fingerprint Hash Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FINGERPRINT SECURITY FLOW                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. BIOMETRIC CAPTURE                                               │
│     ┌──────────────┐                                                │
│     │  Fingerprint │ ──► External biometric device captures         │
│     │   Scanner    │     fingerprint and generates hash             │
│     └──────────────┘                                                │
│            │                                                        │
│            ▼                                                        │
│  2. HASH INPUT                                                      │
│     ┌──────────────┐                                                │
│     │ User enters  │     Hash: a1b2c3d4e5f6...                     │
│     │ fingerprint  │     (64 character hex string)                  │
│     │    hash      │                                                │
│     └──────────────┘                                                │
│            │                                                        │
│            ▼                                                        │
│  3. ID ENCRYPTION                                                   │
│     ┌──────────────────────────────────────┐                       │
│     │ IDs encrypted with fingerprint hash  │                       │
│     │ using AES-256-CBC encryption         │                       │
│     └──────────────────────────────────────┘                       │
│            │                                                        │
│            ▼                                                        │
│  4. BLOCKCHAIN STORAGE                                              │
│     ┌──────────────────────────────────────┐                       │
│     │ Fingerprint hash + ENCRYPTED IDs     │                       │
│     │ stored in immutable blockchain block │                       │
│     └──────────────────────────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Why This is Secure

1. **Biometric Binding**: The fingerprint hash can only be generated from the actual fingerprint
2. **Encrypted ID Storage**: IDs are AES-256 encrypted - unreadable without the fingerprint
3. **No Raw Biometrics Stored**: Only hashes are stored, never actual fingerprint images
4. **Fingerprint = Decryption Key**: Only the user can decrypt their own IDs
5. **Immutable Storage**: Blockchain ensures data cannot be tampered with
6. **Access Control**: Even viewing the blockchain shows only encrypted data

---

## ⛓️ How the Blockchain Works

### Block Structure

Each block in the chain contains:

```
┌─────────────────────────────────────────────┐
│                   BLOCK #N                   │
├─────────────────────────────────────────────┤
│  Index:          N (position in chain)       │
│  Timestamp:      1706640000.123456           │
│  Previous Hash:  0a1b2c3d4e5f... (Block N-1) │
│  Nonce:          12847 (proof of work)       │
│  Hash:           00a7b8c9d0e1... (this block)│
├─────────────────────────────────────────────┤
│  DATA:                                       │
│  {                                           │
│    "type": "fingerprint_record",             │
│    "fingerprint_hash": "a1b2c3...",          │
│    "encrypted_ids": "BASE64_ENCRYPTED...",   │  ← ENCRYPTED!
│    "id_types": ["PASSPORT", "BCID"],         │
│    "record_timestamp": 1706640000.0          │
│  }                                           │
└─────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│                  BLOCK #N+1                  │
│  Previous Hash:  00a7b8c9d0e1... (Block N)  │
│  ...                                         │
└─────────────────────────────────────────────┘
```

### Cryptographic Chain

```
Genesis Block          Block 1              Block 2
┌──────────┐       ┌──────────┐        ┌──────────┐
│ Hash: H0 │◄──────│Prev: H0  │◄───────│Prev: H1  │
│          │       │ Hash: H1 │        │ Hash: H2 │
│ Data: {} │       │ Data:... │        │ Data:... │
└──────────┘       └──────────┘        └──────────┘
```

### How Mining Works (Proof of Work)

Mining ensures blocks are difficult to create, preventing spam and tampering:

```python
# Mining difficulty = 2 means hash must start with "00"
# Difficulty = 4 means hash must start with "0000"

while hash[:difficulty] != "0" * difficulty:
    nonce += 1
    hash = SHA256(block_data + nonce)
```

**Why This Matters:**
- Creating a block requires computational work
- Tampering with one block invalidates all subsequent blocks
- An attacker would need to re-mine the entire chain

### Chain Validation

The blockchain is valid only if:
1. Each block's hash matches its calculated hash
2. Each block's `previous_hash` matches the prior block's hash
3. All hashes meet the difficulty requirement

---

## 🔐 Encryption & Hashing Details

### Algorithms Used

| Purpose | Algorithm | Details |
|---------|-----------|---------|
| Block Hashing | SHA-256 | 256-bit cryptographic hash |
| Fingerprint Storage | SHA-256 | One-way hash, cannot be reversed |
| **ID Encryption** | **AES-256-CBC** | Symmetric encryption with fingerprint hash as key |
| Key Derivation | PBKDF2-like | 10,000 iterations for brute-force resistance |
| Data Integrity | SHA-256 | Any change = different hash |

### ID Encryption Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ID ENCRYPTION FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: ID Data (PASSPORT, BCID)                                │
│  {                                                              │
│    "PASSPORT": {"id": "123456789", "metadata": {...}},         │
│    "BCID": {"id": "987654321", "metadata": {...}}              │
│  }                                                              │
│                │                                                │
│                ▼                                                │
│  KEY DERIVATION                                                 │
│  ┌─────────────────────────────────────┐                       │
│  │  salt = random(16 bytes)            │                       │
│  │  key = PBKDF2(fingerprint_hash,     │                       │
│  │              salt, 10000 iterations)│                       │
│  └─────────────────────────────────────┘                       │
│                │                                                │
│                ▼                                                │
│  AES-256-CBC ENCRYPTION                                         │
│  ┌─────────────────────────────────────┐                       │
│  │  iv = random(16 bytes)              │                       │
│  │  ciphertext = AES_CBC(key, iv, data)│                       │
│  └─────────────────────────────────────┘                       │
│                │                                                │
│                ▼                                                │
│  OUTPUT: Base64(salt + iv + ciphertext)                        │
│  "QUJDREVG..." (stored on blockchain)                          │
│                                                                 │
│  ⚠️  WITHOUT THE FINGERPRINT HASH, DATA CANNOT BE DECRYPTED    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Hash Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      HASHING FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: User fingerprint hash                                   │
│         "a1b2c3d4e5f6g7h8..."                                   │
│                │                                                │
│                ▼                                                │
│  ┌─────────────────────────────────────┐                       │
│  │  IF FP_SECRET_SALT is set:          │                       │
│  │  SHA256("salt:a1b2c3d4e5f6g7h8...") │                       │
│  │  = "f9e8d7c6b5a4..."                │                       │
│  └─────────────────────────────────────┘                       │
│                │                                                │
│                ▼                                                │
│  STORED IN BLOCK DATA                                           │
│  {                                                              │
│    "fingerprint_hash": "f9e8d7c6b5a4...",                      │
│    "encrypted_ids": "BASE64_ENCRYPTED_DATA...",                │
│    "id_types": ["PASSPORT", "BCID"]                            │
│  }                                                              │
│                │                                                │
│                ▼                                                │
│  BLOCK HASH CALCULATION                                         │
│  SHA256(index + timestamp + data + prev_hash + nonce)           │
│  = "00a7b8c9d0e1f2..." (meets difficulty requirement)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

```sql
-- Stores the blockchain blocks
blocks
├── id (PRIMARY KEY)
├── block_index (position in blockchain)
├── timestamp (when block was created)
├── data (JSON: fingerprint_hash, encrypted_ids, id_types)
├── previous_hash (link to previous block)
├── nonce (proof of work value)
├── hash (this block's hash)
└── created_at

-- Denormalized for fast fingerprint queries
fingerprint_records
├── id (PRIMARY KEY)
├── block_id (FOREIGN KEY → blocks)
├── fingerprint_hash (for lookup)
├── record_timestamp
└── created_at

-- One-to-many relationship with fingerprints
id_numbers
├── id (PRIMARY KEY)
├── fingerprint_record_id (FOREIGN KEY)
├── id_number (e.g., "PASSPORT123")
└── created_at

-- Audit trail for all actions
audit_log
├── id (PRIMARY KEY)
├── action (what happened)
├── details (JSON metadata)
└── created_at
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FP_DB_PATH` | `fingerprint_blockchain.db` | Path to SQLite database file |
| `FP_DIFFICULTY` | `2` | Mining difficulty (1-6). Higher = slower but more secure |
| `FP_SECRET_SALT` | *(empty)* | Optional salt for additional fingerprint hash security |

### Setting Environment Variables

**Local (Terminal):**
```bash
export FP_DB_PATH=/path/to/database.db
export FP_DIFFICULTY=3
export FP_SECRET_SALT=my-super-secret-salt-12345
python3 main.py
```

**Docker (docker-compose.yml):**
```yaml
environment:
  - FP_DB_PATH=/app/data/blockchain.db
  - FP_DIFFICULTY=2
  - FP_SECRET_SALT=production-salt-value
```

**Makefile:**
```bash
FP_SECRET_SALT=mysalt make run
```

### When to Use FP_SECRET_SALT

- **Development**: Leave empty (simpler testing)
- **Production**: Always set a strong random value
- **Important**: Once set, never change it or existing data becomes inaccessible!

---

## 🚀 Quick Start

### Run Locally

```bash
# Run the interactive application
make run

# Or with environment variables
FP_DIFFICULTY=3 make run

# Or directly with Python
python3 main.py
```

### Run with Docker

```bash
# Build and run in Docker
make build
make run-docker
```

---

## 🎮 Usage Flow

### 1. Registration Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Step 1: User scans fingerprint on biometric device            │
│          Device outputs: "a1b2c3d4e5f6..."                     │
│                                                                │
│  Step 2: User enters fingerprint hash in application           │
│          > Fingerprint hash: a1b2c3d4e5f6...                   │
│                                                                │
│  Step 3: User enters ID numbers to associate                   │
│          > ID number(s): PASSPORT123, DL456, SSN789            │
│                                                                │
│  Step 4: System creates blockchain block:                      │
│          - Hashes fingerprint (with optional salt)             │
│          - Packages data with timestamp                        │
│          - Mines block (proof of work)                         │
│          - Adds to blockchain                                  │
│          - Saves to database                                   │
│                                                                │
│  Result: Data immutably stored, linked to fingerprint          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 2. Secure Access Flow (Retrieving Data)

```
┌────────────────────────────────────────────────────────────────┐
│                    ACCESS FLOW                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Step 1: User wants to access their stored IDs                 │
│                                                                │
│  Step 2: User scans fingerprint on biometric device            │
│          Device outputs: "a1b2c3d4e5f6..."                     │
│                                                                │
│  Step 3: User enters fingerprint hash in application           │
│          > Option 3: 🔒 Access my records (by fingerprint)     │
│          > Fingerprint hash: a1b2c3d4e5f6...                   │
│                                                                │
│  Step 4: System searches blockchain:                           │
│          - Applies salt (if configured)                        │
│          - Searches for matching fingerprint hash              │
│          - Returns all associated records                      │
│                                                                │
│  Result: ✅ Only the fingerprint owner can access their data   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Menu Options

```
1. Register new fingerprint + IDs    → Store new identity data
2. Search by ID number               → Find records by ID (admin)
3. 🔒 Access my records (by fingerprint) → Secure user access
4. View all records                  → List all stored records
5. View blockchain                   → Display full chain
6. Verify blockchain integrity       → Check for tampering
7. Show statistics                   → Database stats
8. Exit
```

---

## 🔧 Makefile Commands

| Command | Description |
|---------|-------------|
| `make run` | Run application locally |
| `make run-quick` | Quick register mode |
| `make test` | Run tests |
| `make build` | Build Docker image |
| `make run-docker` | Run in Docker |
| `make shell` | Open shell in Docker |
| `make stop` | Stop Docker container |
| `make verify` | Verify blockchain integrity |
| `make db-stats` | Show database statistics |
| `make clean` | Remove database and cache |
| `make clean-docker` | Remove Docker resources |
| `make export` | Export blockchain to JSON |

---

## 📝 Example Session

```
🔐 Fingerprint Identity Blockchain System
==================================================
Initializing...
🆕 Created new blockchain with genesis block
✅ System ready!
   - Blocks in chain: 1
   - Mining difficulty: 2
==================================================

==================================================
📋 MAIN MENU
==================================================
1. Register new fingerprint + IDs
2. Search by ID number
3. 🔒 Access my records (by fingerprint)
4. View all records
5. View blockchain
6. Verify blockchain integrity
7. Show statistics
8. Exit
--------------------------------------------------
Select option (1-8): 1

📱 FINGERPRINT CAPTURE
------------------------------
Enter your fingerprint hash from your biometric device.
This hash securely maps your fingerprint to your identity data.

💡 Tip: Your fingerprint scanner should provide this hash.
        Example format: a1b2c3d4e5f6... (64 hex characters)

Fingerprint hash: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
✅ Fingerprint hash accepted!
   Secure Hash: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4...

🆔 ENTER ID NUMBERS
------------------------------
Enter ID number(s) to associate with this fingerprint.
Multiple IDs can be separated by commas or spaces.
Example: ID001, ID002, ID003

ID number(s): PASSPORT123, DL456, SSN789

📋 IDs to register: PASSPORT123, DL456, SSN789
Confirm? (y/n): y

⛓️  ADDING TO BLOCKCHAIN
------------------------------
⛏️  Mining block #1...
✅ Block mined! Hash: 00a7b2c3d4e5f6...

✅ REGISTRATION COMPLETE!
   Block Index: #1
   Block Hash: 00a7b2c3d4e5f6g7h8i9j0k1l2m3n4o5...
   Fingerprint: a1b2c3d4e5f6...
   IDs: PASSPORT123, DL456, SSN789
```

---

## 🔒 Security Notes

### What This Implementation Provides

- ✅ SHA-256 cryptographic hashing
- ✅ Proof-of-work mining
- ✅ Chain validation detects tampering
- ✅ Each block cryptographically linked
- ✅ Optional salt for fingerprint hashes
- ✅ Biometric-based access control

### Production Considerations

For production deployment, consider:

- 🔧 Real fingerprint hardware integration
- 🔧 Distributed/decentralized network
- 🔧 Encryption for data at rest
- 🔧 Network authentication (TLS/SSL)
- 🔧 Key management system
- 🔧 Regular security audits

---

## 📄 License

MIT License - Feel free to use and modify!
