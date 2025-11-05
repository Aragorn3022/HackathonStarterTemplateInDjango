"""
AES256 Encryption utility for chat messages
"""
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
from django.conf import settings
import hashlib


class AESCipher:
    """
    AES256 encryption/decryption utility
    """
    def __init__(self, key=None):
        """
        Initialize with encryption key.
        If no key provided, use from settings or generate a default one.
        """
        if key is None:
            key = settings.ENCRYPTION_KEY if hasattr(settings, 'ENCRYPTION_KEY') else 'your_encryption_key'
        
        # Ensure key is exactly 32 bytes for AES256
        self.key = hashlib.sha256(key.encode()).digest()
    
    def encrypt(self, plaintext):
        """
        Encrypt plaintext string using AES256
        Returns base64 encoded string
        """
        if not plaintext:
            return ''
        
        # Generate random IV (Initialization Vector)
        iv = get_random_bytes(AES.block_size)
        
        # Create cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Pad and encrypt
        padded_text = pad(plaintext.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_text)
          # Combine IV and encrypted data, then base64 encode
        result = base64.b64encode(iv + encrypted).decode('utf-8')
        return result
    
    def decrypt(self, ciphertext):
        """
        Decrypt base64 encoded ciphertext
        Returns plaintext string
        """
        if not ciphertext:
            return ''
        
        try:
            # Decode base64
            data = base64.b64decode(ciphertext)
            
            # Extract IV and encrypted data
            iv = data[:AES.block_size]
            encrypted = data[AES.block_size:]
            
            # Create cipher and decrypt
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
            
            return decrypted.decode('utf-8')
        except Exception as e:
            import traceback
            print(f"❌ Decryption error: {e}")
            print(f"   Ciphertext (first 50 chars): {ciphertext[:50]}")
            print(f"   Key (hash): {self.key.hex()[:20]}...")
            traceback.print_exc()
            return '[Unable to decrypt message]'


# Global cipher instance
cipher = AESCipher()


def encrypt_message(message):
    """
    Convenience function to encrypt a message
    """
    return cipher.encrypt(message)


def decrypt_message(encrypted_message):
    """
    Convenience function to decrypt a message
    """
    return cipher.decrypt(encrypted_message)
