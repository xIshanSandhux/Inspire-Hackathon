"""
Simple Blockchain Implementation for Fingerprint Identity Storage

Security Features:
- SHA-256 cryptographic hashing for blocks
- Proof-of-work mining for tamper resistance
- Encrypted ID storage (IDs are encrypted with fingerprint hash as key)
"""
import hashlib
import json
import time
from typing import List, Optional, Dict, Any

from encryption import encrypt_ids, decrypt_ids, format_id_for_display


class Block:
    """Represents a single block in the blockchain."""
    
    def __init__(self, index: int, timestamp: float, data: dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the SHA-256 hash of this block."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4) -> None:
        """Mine the block by finding a hash with required difficulty (leading zeros)."""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> dict:
        """Convert block to dictionary for storage."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }
    
    @classmethod
    def from_dict(cls, block_dict: dict) -> 'Block':
        """Create a Block from a dictionary."""
        block = cls(
            index=block_dict["index"],
            timestamp=block_dict["timestamp"],
            data=block_dict["data"],
            previous_hash=block_dict["previous_hash"]
        )
        block.nonce = block_dict["nonce"]
        block.hash = block_dict["hash"]
        return block


class Blockchain:
    """Simple blockchain for storing fingerprint identity records."""
    
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_data: List[dict] = []
    
    def create_genesis_block(self) -> Block:
        """Create the first block in the chain."""
        genesis_block = Block(0, time.time(), {"message": "Genesis Block"}, "0")
        genesis_block.mine_block(self.difficulty)
        return genesis_block
    
    def initialize_chain(self) -> None:
        """Initialize the blockchain with genesis block if empty."""
        if len(self.chain) == 0:
            self.chain.append(self.create_genesis_block())
    
    def get_latest_block(self) -> Optional[Block]:
        """Get the most recent block in the chain."""
        if len(self.chain) == 0:
            return None
        return self.chain[-1]
    
    def add_fingerprint_record(self, fingerprint_hash: str, id_data: Dict[str, Any], 
                                timestamp: Optional[float] = None) -> Block:
        """
        Add a new fingerprint record to the blockchain.
        
        Args:
            fingerprint_hash: Hash of the fingerprint data
            id_data: Dictionary of ID types with id and metadata
                     Format: {"PASSPORT": {"id": "123", "metadata": {...}}, ...}
            timestamp: Optional timestamp (uses current time if not provided)
        
        Returns:
            The newly created and mined block
        
        Security:
            The id_data is encrypted using the fingerprint_hash as the key.
            Only someone with the correct fingerprint hash can decrypt the IDs.
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Encrypt the ID data using fingerprint hash as the key
        encrypted_ids = encrypt_ids(id_data, fingerprint_hash)
        
        data = {
            "type": "fingerprint_record",
            "fingerprint_hash": fingerprint_hash,
            "encrypted_ids": encrypted_ids,  # IDs are stored encrypted
            "id_types": list(id_data.keys()),  # Store which ID types exist (not sensitive)
            "record_timestamp": timestamp
        }
        
        latest_block = self.get_latest_block()
        if latest_block is None:
            self.initialize_chain()
            latest_block = self.get_latest_block()
        
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=latest_block.hash
        )
        
        print(f"⛏️  Mining block #{new_block.index}...")
        new_block.mine_block(self.difficulty)
        print(f"✅ Block mined! Hash: {new_block.hash[:16]}...")
        
        self.chain.append(new_block)
        return new_block
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain integrity."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Invalid hash at block {i}")
                return False
            
            # Check if previous hash reference is correct
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Invalid previous hash reference at block {i}")
                return False
        
        return True
    
    def get_all_fingerprint_records(self) -> List[dict]:
        """Get all fingerprint records from the blockchain (IDs remain encrypted)."""
        records = []
        for block in self.chain:
            if block.data.get("type") == "fingerprint_record":
                records.append({
                    "block_index": block.index,
                    "block_hash": block.hash,
                    "fingerprint_hash": block.data["fingerprint_hash"],
                    "id_types": block.data.get("id_types", []),
                    "encrypted_ids": block.data.get("encrypted_ids", ""),
                    "timestamp": block.data["record_timestamp"]
                })
        return records
    
    def find_record_by_id_type(self, id_type: str) -> List[dict]:
        """Find all records containing a specific ID type (PASSPORT, BCID)."""
        records = []
        for block in self.chain:
            if block.data.get("type") == "fingerprint_record":
                if id_type in block.data.get("id_types", []):
                    records.append({
                        "block_index": block.index,
                        "block_hash": block.hash,
                        "fingerprint_hash": block.data["fingerprint_hash"],
                        "id_types": block.data.get("id_types", []),
                        "encrypted_ids": block.data.get("encrypted_ids", ""),
                        "timestamp": block.data["record_timestamp"]
                    })
        return records
    
    def find_record_by_fingerprint(self, fingerprint_hash: str) -> List[dict]:
        """
        Find all records matching a specific fingerprint hash.
        
        This is the secure access method - only someone with the correct
        fingerprint hash can retrieve their associated identity records.
        The IDs are decrypted using the fingerprint hash.
        
        Args:
            fingerprint_hash: The SHA-256 hash of the user's fingerprint
        
        Returns:
            List of records associated with this fingerprint (with decrypted IDs)
        """
        records = []
        for block in self.chain:
            if block.data.get("type") == "fingerprint_record":
                if block.data.get("fingerprint_hash") == fingerprint_hash:
                    # Decrypt the IDs using the fingerprint hash
                    encrypted_ids = block.data.get("encrypted_ids", "")
                    decrypted_ids = None
                    if encrypted_ids:
                        decrypted_ids = decrypt_ids(encrypted_ids, fingerprint_hash)
                    
                    records.append({
                        "block_index": block.index,
                        "block_hash": block.hash,
                        "fingerprint_hash": block.data["fingerprint_hash"],
                        "id_types": block.data.get("id_types", []),
                        "id_data": decrypted_ids,  # Decrypted ID data
                        "timestamp": block.data["record_timestamp"]
                    })
        return records
    
    def to_json(self) -> str:
        """Export blockchain to JSON string."""
        return json.dumps([block.to_dict() for block in self.chain], indent=2)
    
    def load_from_json(self, json_str: str) -> None:
        """Load blockchain from JSON string."""
        blocks_data = json.loads(json_str)
        self.chain = [Block.from_dict(block_data) for block_data in blocks_data]
    
    def print_chain(self) -> None:
        """Print the entire blockchain in a readable format."""
        print("\n" + "=" * 60)
        print("🔗 BLOCKCHAIN STATUS")
        print("=" * 60)
        print(f"Total blocks: {len(self.chain)}")
        print(f"Chain valid: {'✅ Yes' if self.is_chain_valid() else '❌ No'}")
        print("=" * 60)
        
        for block in self.chain:
            print(f"\n📦 Block #{block.index}")
            print(f"   Timestamp: {time.ctime(block.timestamp)}")
            print(f"   Hash: {block.hash[:32]}...")
            print(f"   Previous: {block.previous_hash[:32]}...")
            print(f"   Nonce: {block.nonce}")
            if block.data.get("type") == "fingerprint_record":
                print(f"   📍 Fingerprint: {block.data['fingerprint_hash'][:16]}...")
                id_types = block.data.get('id_types', [])
                print(f"   🆔 ID Types: {', '.join(id_types) if id_types else 'N/A'}")
                print(f"   🔐 IDs: [ENCRYPTED]")
        
        print("\n" + "=" * 60)
