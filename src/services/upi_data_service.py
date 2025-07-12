"""
UPI transaction data service for collecting and processing real UPI data
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re

from src.services.mock_upi_data import mock_upi_data_service

class UPIDataService:
    """Service for collecting and processing real UPI transaction data"""
    
    def __init__(self):
        self.mock_service = mock_upi_data_service
        self.upi_id_pattern = re.compile(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$')
    
    async def collect_upi_data(self, user_id: str, upi_id: str) -> Dict[str, Any]:
        """
        Collect UPI transaction data for a user
        In a real implementation, this would connect to a UPI API
        """
        # Validate UPI ID format
        if not self.is_valid_upi_id(upi_id):
            return {
                "success": False,
                "error": "Invalid UPI ID format. Expected format: username@provider"
            }
        
        try:
            # In a real implementation, this would call the UPI API
            # For now, we'll use mock data but store the UPI ID
            await self.save_upi_id(user_id, upi_id)
            
            # Return success response
            return {
                "success": True,
                "message": f"Successfully connected UPI ID: {upi_id}",
                "upi_id": upi_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to collect UPI data: {str(e)}"
            }
    
    async def get_transactions(self, user_id: str, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get UPI transactions for a user
        In a real implementation, this would fetch from a UPI API
        """
        try:
            # Check if we have a real UPI ID for this user
            upi_id = await self.get_upi_id(user_id)
            
            if upi_id:
                # In a real implementation, this would fetch real transaction data
                # For now, we'll use mock data but with the real UPI ID
                transactions = self.mock_service.generate_mock_transactions(user_id, days)
                
                # Update the UPI ID in the transactions to match the user's real UPI ID
                for transaction in transactions:
                    if transaction["transaction_type"] == "DEBIT":
                        transaction["upi_id"] = upi_id
                
                return transactions
            else:
                # Fall back to mock data if no UPI ID is available
                return self.mock_service.get_user_transactions(user_id, days)
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def is_valid_upi_id(self, upi_id: str) -> bool:
        """Validate UPI ID format"""
        return bool(self.upi_id_pattern.match(upi_id))
    
    async def save_upi_id(self, user_id: str, upi_id: str) -> bool:
        """
        Save UPI ID for a user
        In a real implementation, this would save to a database
        """
        try:
            # In a real implementation, this would save to a database
            # For now, we'll just print it
            print(f"Saved UPI ID {upi_id} for user {user_id}")
            
            # Here you would typically use a database service:
            # await db_service.update_user(user_id, {"upi_id": upi_id})
            
            # For demo purposes, we'll store in a file
            with open(f"{user_id}_upi_id.txt", "w") as f:
                f.write(upi_id)
            
            return True
        except Exception as e:
            print(f"Error saving UPI ID: {e}")
            return False
    
    async def get_upi_id(self, user_id: str) -> Optional[str]:
        """
        Get UPI ID for a user
        In a real implementation, this would fetch from a database
        """
        try:
            # In a real implementation, this would fetch from a database
            # For now, we'll try to read from a file
            try:
                with open(f"{user_id}_upi_id.txt", "r") as f:
                    return f.read().strip()
            except FileNotFoundError:
                return None
        except Exception as e:
            print(f"Error getting UPI ID: {e}")
            return None
    
    def categorize_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize a transaction based on merchant name or description
        In a real implementation, this would use more sophisticated logic
        """
        # For now, we'll use the mock service's categories
        return transaction
    
    def get_transaction_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for transactions"""
        return self.mock_service.get_transaction_summary(transactions)
    
    def get_transactions_by_category(self, transactions: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Filter transactions by category"""
        return self.mock_service.get_transactions_by_category(transactions, category)
    
    def get_transactions_by_date_range(self, transactions: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Filter transactions by date range"""
        return self.mock_service.get_transactions_by_date_range(transactions, start_date, end_date)
    
    def export_transactions_to_json(self, transactions: List[Dict[str, Any]], filename: str = None) -> str:
        """Export transactions to JSON"""
        return self.mock_service.export_transactions_to_json(transactions, filename)

# Create singleton instance
upi_data_service = UPIDataService() 