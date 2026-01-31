"""
Database module for persistent storage of blockchain and fingerprint records.
Uses SQLite for simplicity and portability.
"""
import sqlite3
import json
import os
from typing import Optional, List
from datetime import datetime


class Database:
    """SQLite database for storing blockchain and fingerprint records."""
    
    def __init__(self, db_path: str = "fingerprint_blockchain.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self) -> None:
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def _create_tables(self) -> None:
        """Create the database schema."""
        cursor = self.connection.cursor()
        
        # Table for blockchain blocks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_index INTEGER NOT NULL UNIQUE,
                timestamp REAL NOT NULL,
                data TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                nonce INTEGER NOT NULL,
                hash TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for fingerprint records (denormalized for easy querying)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fingerprint_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_id INTEGER NOT NULL,
                fingerprint_hash TEXT NOT NULL,
                record_timestamp REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (block_id) REFERENCES blocks(id)
            )
        ''')
        
        # Table for ID numbers (many IDs per fingerprint record)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS id_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint_record_id INTEGER NOT NULL,
                id_number TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fingerprint_record_id) REFERENCES fingerprint_records(id)
            )
        ''')
        
        # Table for audit log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_block_hash ON blocks(hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fingerprint_hash ON fingerprint_records(fingerprint_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_id_number ON id_numbers(id_number)')
        
        self.connection.commit()
    
    def save_block(self, block_dict: dict) -> int:
        """Save a block to the database."""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO blocks 
            (block_index, timestamp, data, previous_hash, nonce, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            block_dict['index'],
            block_dict['timestamp'],
            json.dumps(block_dict['data']),
            block_dict['previous_hash'],
            block_dict['nonce'],
            block_dict['hash']
        ))
        
        self.connection.commit()
        block_id = cursor.lastrowid
        
        # If this is a fingerprint record, save to denormalized tables
        data = block_dict['data']
        if data.get('type') == 'fingerprint_record':
            self._save_fingerprint_record(block_id, data)
        
        # Log the action
        self._log_action('BLOCK_SAVED', f"Block #{block_dict['index']} saved with hash {block_dict['hash'][:16]}...")
        
        return block_id
    
    def _save_fingerprint_record(self, block_id: int, data: dict) -> None:
        """Save fingerprint record to denormalized tables."""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO fingerprint_records 
            (block_id, fingerprint_hash, record_timestamp)
            VALUES (?, ?, ?)
        ''', (
            block_id,
            data['fingerprint_hash'],
            data['record_timestamp']
        ))
        
        record_id = cursor.lastrowid
        
        # Save each ID type (not the actual encrypted IDs, just the types for indexing)
        for id_type in data.get('id_types', []):
            cursor.execute('''
                INSERT INTO id_numbers (fingerprint_record_id, id_number)
                VALUES (?, ?)
            ''', (record_id, id_type))
        
        self.connection.commit()
    
    def load_all_blocks(self) -> List[dict]:
        """Load all blocks from the database."""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM blocks ORDER BY block_index ASC')
        
        blocks = []
        for row in cursor.fetchall():
            blocks.append({
                'index': row['block_index'],
                'timestamp': row['timestamp'],
                'data': json.loads(row['data']),
                'previous_hash': row['previous_hash'],
                'nonce': row['nonce'],
                'hash': row['hash']
            })
        
        return blocks
    
    def get_fingerprint_records(self) -> List[dict]:
        """Get all fingerprint records with their associated ID types (not decrypted values)."""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            SELECT 
                fr.id,
                fr.fingerprint_hash,
                fr.record_timestamp,
                b.hash as block_hash,
                b.block_index,
                b.data as block_data
            FROM fingerprint_records fr
            JOIN blocks b ON fr.block_id = b.id
            ORDER BY fr.record_timestamp DESC
        ''')
        
        records = []
        for row in cursor.fetchall():
            # Get associated ID types
            cursor.execute('''
                SELECT id_number FROM id_numbers 
                WHERE fingerprint_record_id = ?
            ''', (row['id'],))
            
            id_types = [r['id_number'] for r in cursor.fetchall()]
            
            records.append({
                'fingerprint_hash': row['fingerprint_hash'],
                'timestamp': row['record_timestamp'],
                'block_hash': row['block_hash'],
                'block_index': row['block_index'],
                'id_types': id_types  # These are now ID types (PASSPORT, BCID), not actual values
            })
        
        return records
    
    def find_by_id_number(self, id_number: str) -> List[dict]:
        """Find all records containing a specific ID number."""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            SELECT DISTINCT
                fr.fingerprint_hash,
                fr.record_timestamp,
                b.hash as block_hash,
                b.block_index
            FROM id_numbers idn
            JOIN fingerprint_records fr ON idn.fingerprint_record_id = fr.id
            JOIN blocks b ON fr.block_id = b.id
            WHERE idn.id_number = ?
        ''', (id_number,))
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'fingerprint_hash': row['fingerprint_hash'],
                'timestamp': row['record_timestamp'],
                'block_hash': row['block_hash'],
                'block_index': row['block_index']
            })
        
        return records
    
    def find_by_fingerprint(self, fingerprint_hash: str) -> List[dict]:
        """Find records by fingerprint hash."""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            SELECT 
                fr.id,
                fr.fingerprint_hash,
                fr.record_timestamp,
                b.hash as block_hash,
                b.block_index
            FROM fingerprint_records fr
            JOIN blocks b ON fr.block_id = b.id
            WHERE fr.fingerprint_hash = ?
        ''', (fingerprint_hash,))
        
        records = []
        for row in cursor.fetchall():
            # Get associated ID numbers
            cursor.execute('''
                SELECT id_number FROM id_numbers 
                WHERE fingerprint_record_id = ?
            ''', (row['id'],))
            
            id_numbers = [r['id_number'] for r in cursor.fetchall()]
            
            records.append({
                'fingerprint_hash': row['fingerprint_hash'],
                'timestamp': row['record_timestamp'],
                'block_hash': row['block_hash'],
                'block_index': row['block_index'],
                'id_numbers': id_numbers
            })
        
        return records
    
    def _log_action(self, action: str, details: str = None) -> None:
        """Log an action to the audit log."""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO audit_log (action, details)
            VALUES (?, ?)
        ''', (action, details))
        self.connection.commit()
    
    def get_audit_log(self, limit: int = 50) -> List[dict]:
        """Get recent audit log entries."""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT action, details, created_at 
            FROM audit_log 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        cursor = self.connection.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM blocks')
        block_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM fingerprint_records')
        record_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(DISTINCT id_number) as count FROM id_numbers')
        unique_ids = cursor.fetchone()['count']
        
        return {
            'total_blocks': block_count,
            'total_fingerprint_records': record_count,
            'unique_id_numbers': unique_ids
        }
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()


# Database schema documentation
DB_SCHEMA = """
=== DATABASE SCHEMA ===

TABLE: blocks
    - id: INTEGER PRIMARY KEY
    - block_index: INTEGER UNIQUE (position in blockchain)
    - timestamp: REAL (Unix timestamp when block was created)
    - data: TEXT (JSON string containing block data)
    - previous_hash: TEXT (hash of previous block)
    - nonce: INTEGER (proof of work nonce)
    - hash: TEXT UNIQUE (SHA-256 hash of block)
    - created_at: DATETIME

TABLE: fingerprint_records (denormalized for fast queries)
    - id: INTEGER PRIMARY KEY
    - block_id: INTEGER FOREIGN KEY -> blocks.id
    - fingerprint_hash: TEXT (hash of fingerprint data)
    - record_timestamp: REAL (when fingerprint was captured)
    - created_at: DATETIME

TABLE: id_numbers (one-to-many with fingerprint_records)
    - id: INTEGER PRIMARY KEY
    - fingerprint_record_id: INTEGER FOREIGN KEY -> fingerprint_records.id
    - id_number: TEXT (the actual ID number)
    - created_at: DATETIME

TABLE: audit_log
    - id: INTEGER PRIMARY KEY
    - action: TEXT (type of action performed)
    - details: TEXT (additional details)
    - created_at: DATETIME

INDEXES:
    - idx_block_hash on blocks(hash)
    - idx_fingerprint_hash on fingerprint_records(fingerprint_hash)
    - idx_id_number on id_numbers(id_number)
"""

if __name__ == "__main__":
    print(DB_SCHEMA)
