"""
Authentication middleware and sandbox verification tools.
"""
import secrets
import hashlib
from typing import Optional, Dict, List

class Authenticator:
    """
    Handles authentication and sandbox verification for the Neural Agent Network.
    """
    
    def __init__(self):
        """Initialize the authenticator with an empty token store."""
        self._tokens: Dict[str, dict] = {}
        self._sandbox_keys: Dict[str, str] = {}
        
    def generate_token(self, user_id: str, roles: Optional[List[str]] = None) -> str:
        """
        Generate a secure authentication token for a user.
        
        Args:
            user_id: The unique identifier of the user.
            roles: A list of roles assigned to the user.
            
        Returns:
            A securely generated token string.
        """
        if roles is None:
            roles = []
            
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)
        
        self._tokens[token_hash] = {
            "user_id": user_id,
            "roles": roles
        }
        
        return token
        
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify a token and return the associated user data if valid.
        
        Args:
            token: The token to verify.
            
        Returns:
            The user data dictionary if valid, None otherwise.
        """
        token_hash = self._hash_token(token)
        return self._tokens.get(token_hash)
        
    def register_sandbox(self, sandbox_id: str) -> str:
        """
        Register a new sandbox and generate its verification key.
        
        Args:
            sandbox_id: The unique identifier for the sandbox.
            
        Returns:
            The verification key for the sandbox.
        """
        key = secrets.token_hex(16)
        self._sandbox_keys[sandbox_id] = key
        return key
        
    def verify_sandbox(self, sandbox_id: str, key: str) -> bool:
        """
        Verify a sandbox using its registered key.
        
        Args:
            sandbox_id: The identifier of the sandbox.
            key: The key to verify against.
            
        Returns:
            True if verification succeeds, False otherwise.
        """
        stored_key = self._sandbox_keys.get(sandbox_id)
        if not stored_key:
            return False
            
        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(stored_key, key)
        
    def _hash_token(self, token: str) -> str:
        """
        Create a secure hash of a token.
        
        Args:
            token: The token to hash.
            
        Returns:
            The SHA-256 hash of the token.
        """
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
