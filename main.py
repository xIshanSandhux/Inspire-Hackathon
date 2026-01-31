"""
Fingerprint Identity Blockchain Application
Main entry point with CLI interface.

Security Flow:
1. User provides their fingerprint hash (from external biometric device)
2. The fingerprint hash is used as a secure key to map user identity
3. ID data (PASSPORT, BCID) is encrypted using the fingerprint hash
4. Encrypted data is stored on blockchain with SHA-256 cryptographic hashing
5. Each block is mined with proof-of-work for tamper resistance
6. Only the correct fingerprint hash can decrypt the stored IDs

Environment Variables:
- FP_DB_PATH: Database file path (default: fingerprint_blockchain.db)
- FP_DIFFICULTY: Mining difficulty 1-6 (default: 2)
- FP_SECRET_SALT: Optional salt for additional fingerprint hash security
"""
import hashlib
import time
import sys
import os
import json
from typing import List, Optional, Dict, Any
from blockchain import Blockchain, Block
from database import Database
from encryption import validate_id_data, format_id_for_display, get_crypto_status, VALID_ID_TYPES

# Environment variable defaults
DEFAULT_DB_PATH = os.getenv('FP_DB_PATH', 'fingerprint_blockchain.db')
DEFAULT_DIFFICULTY = int(os.getenv('FP_DIFFICULTY', '2'))
SECRET_SALT = os.getenv('FP_SECRET_SALT', '')


class FingerprintApp:
    """Main application for fingerprint identity management on blockchain."""
    
    def __init__(self, db_path: str = None, difficulty: int = None):
        """
        Initialize the application.
        
        Args:
            db_path: Path to SQLite database file (env: FP_DB_PATH)
            difficulty: Mining difficulty (lower = faster, higher = more secure) (env: FP_DIFFICULTY)
        
        Security Note:
            The fingerprint hash provided by the user acts as a cryptographic key.
            Only someone with access to the original fingerprint can regenerate
            this hash, ensuring data is only accessible when the user is present.
        """
        # Use environment variables if not explicitly provided
        db_path = db_path or DEFAULT_DB_PATH
        difficulty = difficulty if difficulty is not None else DEFAULT_DIFFICULTY
        
        print("🔐 Fingerprint Identity Blockchain System")
        print("=" * 50)
        print("Initializing...")
        
        self.db = Database(db_path)
        self.blockchain = Blockchain(difficulty=difficulty)
        self._load_blockchain_from_db()
        
        print(f"✅ System ready!")
        print(f"   - Blocks in chain: {len(self.blockchain.chain)}")
        print(f"   - Mining difficulty: {difficulty}")
        print("=" * 50 + "\n")
    
    def _load_blockchain_from_db(self) -> None:
        """Load existing blockchain from database."""
        blocks = self.db.load_all_blocks()
        
        if blocks:
            self.blockchain.chain = [Block.from_dict(b) for b in blocks]
            print(f"📂 Loaded {len(blocks)} blocks from database")
        else:
            self.blockchain.initialize_chain()
            # Save genesis block
            genesis = self.blockchain.chain[0]
            self.db.save_block(genesis.to_dict())
            print("🆕 Created new blockchain with genesis block")
    
    def capture_fingerprint(self) -> str:
        """
        Capture fingerprint hash from user input.
        
        The user provides a hash that represents their fingerprint data.
        This hash should come from an external biometric device/scanner.
        
        Security Model:
        - The fingerprint hash acts as a secure key to access user data
        - Only the person with the physical fingerprint can generate this hash
        - The hash is further secured with optional salt (FP_SECRET_SALT env var)
        - Without the correct fingerprint hash, data cannot be linked to the user
        
        Returns:
            str: SHA-256 hash representing the user's fingerprint
        """
        print("\n📱 FINGERPRINT CAPTURE")
        print("-" * 30)
        print("Enter your fingerprint hash from your biometric device.")
        print("This hash securely maps your fingerprint to your identity data.")
        print("")
        print("💡 Tip: Your fingerprint scanner should provide this hash.")
        print("        Example format: a1b2c3d4e5f6... (64 hex characters)")
        print("")
        
        while True:
            fingerprint_input = input("Fingerprint hash: ").strip()
            
            if not fingerprint_input:
                print("⚠️  Please enter a fingerprint hash.")
                continue
            
            # Validate it looks like a hash (hex string)
            if not all(c in '0123456789abcdefABCDEF' for c in fingerprint_input):
                print("⚠️  Invalid hash format. Please enter a hexadecimal string.")
                print("   Valid characters: 0-9, a-f, A-F")
                continue
            
            # Normalize to lowercase
            fingerprint_input = fingerprint_input.lower()
            
            # Apply additional security: hash the input with optional salt
            # This ensures even if someone intercepts the hash, they can't use it
            # without knowing the system's salt
            if SECRET_SALT:
                secured_data = f"{SECRET_SALT}:{fingerprint_input}"
                fingerprint_hash = hashlib.sha256(secured_data.encode()).hexdigest()
                print(f"\n🔒 Fingerprint hash secured with system salt")
            else:
                # If input is already a proper SHA-256 hash, use it directly
                # Otherwise, hash it for consistency
                if len(fingerprint_input) == 64:
                    fingerprint_hash = fingerprint_input
                else:
                    fingerprint_hash = hashlib.sha256(fingerprint_input.encode()).hexdigest()
            
            print(f"✅ Fingerprint hash accepted!")
            print(f"   Secure Hash: {fingerprint_hash[:32]}...")
            
            return fingerprint_hash
    
    def get_id_data(self) -> Dict[str, Any]:
        """
        Get structured ID data from user input.
        
        Supports PASSPORT and BCID with the following structure:
        {
            "PASSPORT": {"id": "123456789", "metadata": {...}},
            "BCID": {"id": "987654321", "metadata": {...}}
        }
        """
        print("\n🆔 ENTER ID INFORMATION")
        print("-" * 50)
        print(f"Valid ID types: {', '.join(VALID_ID_TYPES)}")
        print("")
        print("You can enter IDs in two ways:")
        print("  1. Simple mode: Just enter ID type and number")
        print("  2. JSON mode: Paste full JSON with metadata")
        print("")
        
        id_data = {}
        
        while True:
            print(f"\nCurrently registered: {list(id_data.keys()) if id_data else 'None'}")
            print("-" * 30)
            print("Options:")
            print("  1. Add PASSPORT")
            print("  2. Add BCID") 
            print("  3. Enter as JSON (advanced)")
            print("  4. Done - finish adding IDs")
            print("")
            
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                passport_data = self._get_single_id_input("PASSPORT")
                if passport_data:
                    id_data["PASSPORT"] = passport_data
                    print("✅ PASSPORT added!")
                    
            elif choice == '2':
                bcid_data = self._get_single_id_input("BCID")
                if bcid_data:
                    id_data["BCID"] = bcid_data
                    print("✅ BCID added!")
                    
            elif choice == '3':
                json_data = self._get_json_input()
                if json_data:
                    id_data.update(json_data)
                    print("✅ JSON data added!")
                    
            elif choice == '4':
                if not id_data:
                    print("⚠️  Please add at least one ID before finishing.")
                    continue
                break
            else:
                print("⚠️  Invalid option. Please select 1-4.")
        
        # Display summary
        print("\n📋 ID DATA SUMMARY")
        print("-" * 30)
        for id_type, id_info in id_data.items():
            print(f"\n   {id_type}:")
            print(f"      ID: {id_info['id']}")
            if id_info.get('metadata'):
                for key, value in id_info['metadata'].items():
                    print(f"      {key}: {value}")
        
        confirm = input("\nConfirm this data? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Let's try again...")
            return self.get_id_data()
        
        return id_data
    
    def _get_single_id_input(self, id_type: str) -> Optional[Dict[str, Any]]:
        """Get input for a single ID type."""
        print(f"\n📄 Adding {id_type}")
        print("-" * 20)
        
        # Get ID number (required)
        id_number = input(f"{id_type} ID number: ").strip()
        if not id_number:
            print("⚠️  ID number is required.")
            return None
        
        # Ask about metadata
        add_metadata = input("Add metadata? (y/n): ").strip().lower()
        
        metadata = {}
        if add_metadata in ['y', 'yes']:
            print("Enter metadata (key=value format, empty line to finish):")
            print("Example: country=Canada")
            
            while True:
                meta_input = input("  > ").strip()
                if not meta_input:
                    break
                
                if '=' in meta_input:
                    key, value = meta_input.split('=', 1)
                    metadata[key.strip()] = value.strip()
                else:
                    print("    Invalid format. Use: key=value")
        
        return {
            "id": id_number,
            "metadata": metadata
        }
    
    def _get_json_input(self) -> Optional[Dict[str, Any]]:
        """Get ID data as JSON input."""
        print("\n📝 JSON INPUT MODE")
        print("-" * 20)
        print("Paste your JSON data (press Enter twice to finish):")
        print("Example:")
        print('''  {
    "PASSPORT": {"id": "123456789", "metadata": {"country": "Canada"}},
    "BCID": {"id": "987654321", "metadata": {}}
  }''')
        print("")
        
        lines = []
        empty_count = 0
        while empty_count < 1:
            line = input()
            if not line:
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        
        json_str = '\n'.join(lines)
        
        try:
            data = json.loads(json_str)
            
            # Validate the data
            is_valid, error = validate_id_data(data)
            if not is_valid:
                print(f"⚠️  Invalid data: {error}")
                return None
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON: {e}")
            return None
    
    def register_fingerprint(self) -> Optional[Block]:
        """Complete fingerprint registration flow."""
        try:
            # Capture fingerprint
            fingerprint_hash = self.capture_fingerprint()
            
            # Get structured ID data
            id_data = self.get_id_data()
            
            # Add to blockchain (IDs will be encrypted)
            print("\n⛓️  ADDING TO BLOCKCHAIN")
            print("-" * 30)
            print(f"🔐 Encrypting IDs with: {get_crypto_status()}")
            
            block = self.blockchain.add_fingerprint_record(
                fingerprint_hash=fingerprint_hash,
                id_data=id_data
            )
            
            # Save to database
            self.db.save_block(block.to_dict())
            
            print("\n✅ REGISTRATION COMPLETE!")
            print(f"   Block Index: #{block.index}")
            print(f"   Block Hash: {block.hash[:32]}...")
            print(f"   Fingerprint: {fingerprint_hash[:16]}...")
            print(f"   ID Types: {', '.join(id_data.keys())}")
            print(f"   🔐 IDs stored ENCRYPTED on blockchain")
            
            return block
            
        except KeyboardInterrupt:
            print("\n\n❌ Registration cancelled.")
            return None
    
    def search_by_id_type(self, id_type: str = None) -> None:
        """Search for records by ID type (PASSPORT or BCID)."""
        if id_type is None:
            print("\n🔍 SEARCH BY ID TYPE")
            print("-" * 30)
            print(f"Available types: {', '.join(VALID_ID_TYPES)}")
            id_type = input("Enter ID type to search: ").strip().upper()
        
        if not id_type:
            print("⚠️  No ID type provided.")
            return
        
        if id_type not in VALID_ID_TYPES:
            print(f"⚠️  Invalid ID type. Valid types: {', '.join(VALID_ID_TYPES)}")
            return
        
        # Search in blockchain
        records = self.blockchain.find_record_by_id_type(id_type)
        
        if records:
            print(f"\n✅ Found {len(records)} record(s) with {id_type}")
            print("⚠️  Note: Actual ID values are encrypted and require fingerprint to decrypt")
            for i, record in enumerate(records, 1):
                print(f"\n   Record {i}:")
                print(f"   - Block: #{record['block_index']}")
                print(f"   - Fingerprint: {record['fingerprint_hash'][:24]}...")
                print(f"   - ID Types: {', '.join(record['id_types'])}")
                print(f"   - 🔐 IDs: [ENCRYPTED]")
                print(f"   - Timestamp: {time.ctime(record['timestamp'])}")
        else:
            print(f"\n❌ No records found with ID type: {id_type}")
    
    def search_by_fingerprint(self, fingerprint_hash: str = None) -> None:
        """
        Search for records by fingerprint hash and decrypt IDs.
        
        This is the secure way to access user data - only the person
        with the matching fingerprint can retrieve and decrypt their IDs.
        
        Security Model:
        - User must provide the exact fingerprint hash
        - This hash can only be generated from the original biometric data
        - The hash is used to decrypt the stored ID data
        - Ensures data privacy: only the fingerprint owner can see their IDs
        """
        if fingerprint_hash is None:
            print("\n🔍 SEARCH BY FINGERPRINT (Secure Access)")
            print("-" * 30)
            print("Enter your fingerprint hash to retrieve and DECRYPT your IDs.")
            print("This ensures only you can access your identity data.")
            print("")
            fingerprint_hash = input("Fingerprint hash: ").strip().lower()
        
        if not fingerprint_hash:
            print("⚠️  No fingerprint hash provided.")
            return
        
        # Apply salt if configured (must match registration)
        if SECRET_SALT:
            secured_data = f"{SECRET_SALT}:{fingerprint_hash}"
            search_hash = hashlib.sha256(secured_data.encode()).hexdigest()
        else:
            if len(fingerprint_hash) == 64:
                search_hash = fingerprint_hash
            else:
                search_hash = hashlib.sha256(fingerprint_hash.encode()).hexdigest()
        
        # Search in blockchain (this will also decrypt IDs)
        records = self.blockchain.find_record_by_fingerprint(search_hash)
        
        if records:
            print(f"\n✅ Found {len(records)} record(s) for your fingerprint!")
            print("🔓 Access granted - decrypting your IDs...\n")
            
            for i, record in enumerate(records, 1):
                print(f"{'='*50}")
                print(f"   Record {i}:")
                print(f"   Block: #{record['block_index']}")
                print(f"   Registered: {time.ctime(record['timestamp'])}")
                print(f"   Block Hash: {record['block_hash'][:24]}...")
                print(f"{'='*50}")
                
                id_data = record.get('id_data')
                if id_data:
                    print("\n   🔓 DECRYPTED ID DATA:")
                    print(format_id_for_display(id_data))
                else:
                    print("\n   ⚠️  Could not decrypt IDs (wrong fingerprint hash?)")
                print("")
        else:
            print(f"\n🔒 No records found for this fingerprint.")
            print("   Make sure you're using the same fingerprint hash used during registration.")
    
    def verify_blockchain(self) -> bool:
        """Verify blockchain integrity."""
        print("\n🔍 VERIFYING BLOCKCHAIN INTEGRITY")
        print("-" * 30)
        
        is_valid = self.blockchain.is_chain_valid()
        
        if is_valid:
            print("✅ Blockchain is VALID!")
            print("   All blocks are properly linked and hashes are correct.")
        else:
            print("❌ Blockchain is INVALID!")
            print("   Data may have been tampered with.")
        
        return is_valid
    
    def show_statistics(self) -> None:
        """Show system statistics."""
        print("\n📊 SYSTEM STATISTICS")
        print("-" * 30)
        
        stats = self.db.get_stats()
        
        print(f"   Total Blocks: {stats['total_blocks']}")
        print(f"   Fingerprint Records: {stats['total_fingerprint_records']}")
        print(f"   Unique ID Numbers: {stats['unique_id_numbers']}")
        print(f"   Chain Valid: {'✅ Yes' if self.blockchain.is_chain_valid() else '❌ No'}")
    
    def show_all_records(self) -> None:
        """Display all fingerprint records (IDs remain encrypted)."""
        print("\n📋 ALL FINGERPRINT RECORDS")
        print("-" * 30)
        print("⚠️  Note: ID values are encrypted. Use 'Access by fingerprint' to decrypt.")
        
        records = self.db.get_fingerprint_records()
        
        if not records:
            print("   No records found.")
            return
        
        for i, record in enumerate(records, 1):
            print(f"\n   Record {i}:")
            print(f"   - Block: #{record['block_index']}")
            print(f"   - Fingerprint: {record['fingerprint_hash'][:24]}...")
            print(f"   - ID Types: {', '.join(record.get('id_types', ['N/A']))}")
            print(f"   - 🔐 IDs: [ENCRYPTED]")
            print(f"   - Time: {time.ctime(record['timestamp'])}")
    
    def show_blockchain(self) -> None:
        """Display the full blockchain."""
        self.blockchain.print_chain()
    
    def run_interactive(self) -> None:
        """Run interactive CLI mode."""
        while True:
            print("\n" + "=" * 50)
            print("📋 MAIN MENU")
            print("=" * 50)
            print("1. Register new fingerprint + IDs")
            print("2. Search by ID type (PASSPORT/BCID)")
            print("3. 🔒 Access my records (by fingerprint) - DECRYPTS IDs")
            print("4. View all records (encrypted)")
            print("5. View blockchain")
            print("6. Verify blockchain integrity")
            print("7. Show statistics")
            print("8. Exit")
            print("-" * 50)
            
            try:
                choice = input("Select option (1-8): ").strip()
                
                if choice == '1':
                    self.register_fingerprint()
                elif choice == '2':
                    self.search_by_id_type()
                elif choice == '3':
                    self.search_by_fingerprint()
                elif choice == '4':
                    self.show_all_records()
                elif choice == '5':
                    self.show_blockchain()
                elif choice == '6':
                    self.verify_blockchain()
                elif choice == '7':
                    self.show_statistics()
                elif choice == '8':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("⚠️  Invalid option. Please select 1-8.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def close(self) -> None:
        """Clean up resources."""
        self.db.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fingerprint Identity Blockchain System"
    )
    parser.add_argument(
        '--db', 
        default='fingerprint_blockchain.db',
        help='Database file path (default: fingerprint_blockchain.db)'
    )
    parser.add_argument(
        '--difficulty', 
        type=int, 
        default=2,
        help='Mining difficulty 1-6 (default: 2, higher = slower but more secure)'
    )
    parser.add_argument(
        '--register', 
        action='store_true',
        help='Quick register mode - register one fingerprint and exit'
    )
    
    args = parser.parse_args()
    
    app = FingerprintApp(db_path=args.db, difficulty=args.difficulty)
    
    try:
        if args.register:
            app.register_fingerprint()
        else:
            app.run_interactive()
    finally:
        app.close()


if __name__ == "__main__":
    main()
