# schema/models.py
from dataclasses import dataclass
from datetime import datetime

import json

import uuid
import random


@dataclass
class Transaction:
    transaction_id: str
    account_id: str
    transaction_type: str
    amount: float
    timestamp: str

    @classmethod
    def create_random(cls):
        """Create a random transaction"""
    
        transaction_types = ['DEPOSIT', 'WITHDRAWAL']
        account_ids = ['ACC123', 'ACC456', 'ACC789']  # Simplified account IDs
        
        return cls(
            transaction_id=str(uuid.uuid4()),
            account_id=random.choice(account_ids),
            transaction_type=random.choice(transaction_types),
            amount=round(random.uniform(10, 5000), 2),
            timestamp=datetime.now().isoformat()
        )

    def to_json(self):
        """Convert transaction to JSON string"""
        return json.dumps(self.__dict__)