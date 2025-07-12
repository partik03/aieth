"""
Mock UPI transaction data service for testing and analysis
"""

import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class MockUPIDataService:
    """Service for generating and managing mock UPI transaction data"""
    
    def __init__(self):
        # Mock merchant database
        self.merchants = {
            "Food & Dining": [
                "Swiggy", "Zomato", "Domino's", "McDonald's", "KFC", "Pizza Hut",
                "Starbucks", "Cafe Coffee Day", "Subway", "Burger King"
            ],
            "Shopping": [
                "Amazon", "Flipkart", "Myntra", "Nykaa", "Ajio", "Reliance Digital",
                "Croma", "Vijay Sales", "Big Bazaar", "DMart"
            ],
            "Transportation": [
                "Uber", "Ola", "Metro", "IRCTC", "RedBus", "MakeMyTrip",
                "Goibibo", "Yatra", "Cleartrip", "RailYatri"
            ],
            "Entertainment": [
                "Netflix", "Amazon Prime", "Disney+ Hotstar", "Zee5", "SonyLIV",
                "BookMyShow", "PVR Cinemas", "INOX", "Carnival Cinemas"
            ],
            "Utilities": [
                "BSES", "Tata Power", "BMC Water", "Airtel", "Jio", "Vi",
                "ACT Fibernet", "Hathway", "Tata Sky", "Dish TV"
            ],
            "Healthcare": [
                "Apollo Pharmacy", "MedPlus", "1mg", "PharmEasy", "Netmeds",
                "Apollo Hospitals", "Fortis", "Max Healthcare"
            ],
            "Education": [
                "Coursera", "Udemy", "edX", "BYJU'S", "Unacademy", "Vedantu",
                "Toppr", "Extramarks", "Meritnation"
            ],
            "Finance": [
                "HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Bank",
                "Paytm", "PhonePe", "Google Pay", "BHIM"
            ],
            "Travel": [
                "Booking.com", "Airbnb", "Goibibo", "MakeMyTrip", "Yatra",
                "Cleartrip", "Expedia", "Agoda", "Trivago"
            ],
            "Other": [
                "General Store", "Local Market", "Petrol Pump", "ATM Withdrawal",
                "Online Services", "Subscription Services"
            ]
        }
        
        # Transaction types
        self.transaction_types = ["DEBIT", "CREDIT"]
        
        # UPI IDs for mock users
        self.upi_ids = [
            "user123@okicici", "user456@paytm", "user789@ybl", "user101@upi",
            "user202@axis", "user303@hdfc", "user404@kotak", "user505@sbi"
        ]
    
    def generate_mock_transactions(
        self, 
        user_id: str, 
        days: int = 90, 
        min_transactions: int = 30,
        max_transactions: int = 150
    ) -> List[Dict[str, Any]]:
        """Generate mock UPI transactions for a user"""
        transactions = []
        
        # Determine number of transactions
        num_transactions = random.randint(min_transactions, max_transactions)
        
        # Generate transactions over the specified period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for _ in range(num_transactions):
            transaction = self._generate_single_transaction(user_id, start_date, end_date)
            transactions.append(transaction)
        
        # Sort by date (newest first)
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        return transactions
    
    def _generate_single_transaction(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate a single mock transaction"""
        # Random date within range
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randint(0, days_between)
        random_date = start_date + timedelta(days=random_days)
        
        # Add random time within the day
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        random_date = random_date.replace(hour=random_hours, minute=random_minutes)
        
        # Determine transaction type (mostly debits, some credits)
        transaction_type = random.choices(
            self.transaction_types, 
            weights=[0.85, 0.15]  # 85% debits, 15% credits
        )[0]
        
        # Select category and merchant
        category = random.choice(list(self.merchants.keys()))
        merchant = random.choice(self.merchants[category])
        
        # Generate amount based on category
        amount = self._generate_amount_for_category(category, transaction_type)
        
        # Generate UPI ID
        upi_id = random.choice(self.upi_ids)
        
        # Generate transaction ID
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        
        # Generate reference number
        reference = f"REF{random.randint(100000000, 999999999)}"
        
        # Determine status (mostly successful)
        status = random.choices(
            ["SUCCESS", "FAILED", "PENDING"], 
            weights=[0.95, 0.03, 0.02]
        )[0]
        
        # Generate remarks
        remarks = self._generate_remarks(category, merchant, transaction_type)
        
        return {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "date": random_date,
            "amount": amount,
            "transaction_type": transaction_type,
            "category": category,
            "merchant": merchant,
            "upi_id": upi_id,
            "reference_number": reference,
            "status": status,
            "remarks": remarks,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_amount_for_category(self, category: str, transaction_type: str) -> float:
        """Generate realistic amount based on category"""
        if transaction_type == "CREDIT":
            # Credits are usually larger amounts (salary, refunds, etc.)
            if category == "Finance":
                return random.uniform(5000, 50000)
            else:
                return random.uniform(1000, 10000)
        
        # Debit amounts by category
        amount_ranges = {
            "Food & Dining": (50, 2000),
            "Shopping": (100, 5000),
            "Transportation": (20, 500),
            "Entertainment": (100, 2000),
            "Utilities": (500, 3000),
            "Healthcare": (200, 3000),
            "Education": (500, 5000),
            "Finance": (100, 10000),
            "Travel": (1000, 20000),
            "Other": (50, 1000)
        }
        
        min_amount, max_amount = amount_ranges.get(category, (50, 1000))
        return round(random.uniform(min_amount, max_amount), 2)
    
    def _generate_remarks(self, category: str, merchant: str, transaction_type: str) -> str:
        """Generate realistic transaction remarks"""
        if transaction_type == "CREDIT":
            remarks_templates = [
                f"Credit from {merchant}",
                f"Refund from {merchant}",
                f"Salary credit",
                f"Transfer received",
                f"Cashback from {merchant}"
            ]
        else:
            remarks_templates = [
                f"Payment to {merchant}",
                f"UPI payment to {merchant}",
                f"Purchase at {merchant}",
                f"Bill payment to {merchant}",
                f"Transfer to {merchant}"
            ]
        
        return random.choice(remarks_templates)
    
    def get_transaction_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for transactions"""
        if not transactions:
            return {"error": "No transactions found"}
        
        total_amount = sum(t.get('amount', 0) for t in transactions)
        total_count = len(transactions)
        
        # Categorize by type
        debits = [t for t in transactions if t.get('transaction_type') == 'DEBIT']
        credits = [t for t in transactions if t.get('transaction_type') == 'CREDIT']
        
        debit_amount = sum(t.get('amount', 0) for t in debits)
        credit_amount = sum(t.get('amount', 0) for t in credits)
        
        # Category breakdown
        categories = {}
        for transaction in transactions:
            category = transaction.get('category', 'Other')
            amount = transaction.get('amount', 0)
            if category not in categories:
                categories[category] = 0
            categories[category] += amount
        
        # Monthly breakdown
        monthly_data = {}
        for transaction in transactions:
            date = transaction.get('date')
            if isinstance(date, str):
                date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            month_key = date.strftime('%Y-%m')
            amount = transaction.get('amount', 0)
            
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += amount
        
        return {
            "total_transactions": total_count,
            "total_amount": total_amount,
            "debit_transactions": len(debits),
            "debit_amount": debit_amount,
            "credit_transactions": len(credits),
            "credit_amount": credit_amount,
            "net_amount": credit_amount - debit_amount,
            "average_transaction": total_amount / total_count if total_count > 0 else 0,
            "categories": categories,
            "monthly_breakdown": monthly_data,
            "date_range": {
                "start": min(t.get('date') for t in transactions),
                "end": max(t.get('date') for t in transactions)
            }
        }
    
    def get_user_transactions(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get mock transactions for a specific user"""
        return self.generate_mock_transactions(user_id, days)
    
    def get_transactions_by_category(
        self, 
        transactions: List[Dict[str, Any]], 
        category: str
    ) -> List[Dict[str, Any]]:
        """Filter transactions by category"""
        return [t for t in transactions if t.get('category') == category]
    
    def get_transactions_by_date_range(
        self, 
        transactions: List[Dict[str, Any]], 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Filter transactions by date range"""
        filtered_transactions = []
        
        for transaction in transactions:
            transaction_date = transaction.get('date')
            if isinstance(transaction_date, str):
                transaction_date = datetime.fromisoformat(transaction_date.replace('Z', '+00:00'))
            
            if start_date <= transaction_date <= end_date:
                filtered_transactions.append(transaction)
        
        return filtered_transactions
    
    def export_transactions_to_json(
        self, 
        transactions: List[Dict[str, Any]], 
        filename: str = None
    ) -> str:
        """Export transactions to JSON format"""
        if filename is None:
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        export_data = []
        for transaction in transactions:
            export_transaction = transaction.copy()
            if isinstance(export_transaction.get('date'), datetime):
                export_transaction['date'] = export_transaction['date'].isoformat()
            export_data.append(export_transaction)
        
        json_data = json.dumps(export_data, indent=2, default=str)
        
        # In a real application, you would save this to a file
        # For now, we'll just return the JSON string
        return json_data


# Global instance
mock_upi_data_service = MockUPIDataService() 