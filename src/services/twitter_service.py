"""
Twitter service for fetching trending crypto tokens
"""

import asyncio
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
import apscheduler.schedulers.asyncio
from apscheduler.triggers.cron import CronTrigger

from src.services.db import get_collection


class TwitterService:
    """Service for fetching trending crypto tokens from Twitter/X"""
    
    def __init__(self):
        self.collection_name = "trending_tokens"
        self.scheduler = apscheduler.schedulers.asyncio.AsyncIOScheduler()
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """Setup scheduler to fetch trending tokens every hour"""
        self.scheduler.add_job(
            self._fetch_and_save_trending_tokens,
            CronTrigger(minute=0),  # Run every hour at minute 0
            id="fetch_trending_tokens",
            replace_existing=True
        )
    
    def start_scheduler(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("🕐 Twitter trending tokens scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("🛑 Twitter trending tokens scheduler stopped")
    
    async def _fetch_trending_tokens_mock(self) -> List[str]:
        """Mock function to fetch trending tokens (simulates Twitter API)"""
        # Simulate different trending tokens based on time
        hour = datetime.now().hour
        
        # Different trending sets for different times
        trending_sets = [
            ["BTC", "ETH", "DOGE", "MATIC", "SOL", "ADA", "DOT"],
            ["ETH", "MATIC", "SOL", "AVAX", "LINK", "UNI", "AAVE"],
            ["BTC", "ETH", "DOGE", "SHIB", "PEPE", "FLOKI", "BONK"],
            ["ETH", "MATIC", "SOL", "ARB", "OP", "IMX", "MASK"],
            ["BTC", "ETH", "DOGE", "MATIC", "SOL", "LTC", "BCH"],
            ["ETH", "MATIC", "SOL", "AVAX", "FTM", "NEAR", "ATOM"]
        ]
        
        # Select trending set based on hour
        base_tokens = trending_sets[hour % len(trending_sets)]
        
        # Add some randomness
        random.shuffle(base_tokens)
        
        # Return 5-7 trending tokens
        return base_tokens[:random.randint(5, 7)]
    
    async def get_trending_tokens(self) -> List[str]:
        """Get current trending tokens (cached or fresh)"""
        try:
            collection = await get_collection(self.collection_name)
            
            # Get the latest trending tokens from database
            latest_record = await collection.find_one(
                {},
                sort=[("timestamp", -1)]
            )
            
            if latest_record and latest_record.get("tokens"):
                # Check if data is less than 2 hours old
                timestamp = latest_record.get("timestamp")
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                if datetime.now(timestamp.tzinfo) - timestamp < timedelta(hours=2):
                    return latest_record["tokens"]
            
            # If no recent data, fetch fresh tokens
            return await self._fetch_trending_tokens_mock()
            
        except Exception as e:
            print(f"Error getting trending tokens: {e}")
            # Return default trending tokens
            return ["BTC", "ETH", "DOGE", "MATIC", "SOL"]
    
    async def _fetch_and_save_trending_tokens(self):
        """Fetch trending tokens and save to database"""
        try:
            tokens = await self._fetch_trending_tokens_mock()
            
            # Save to database
            collection = await get_collection(self.collection_name)
            await collection.insert_one({
                "tokens": tokens,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "twitter_mock",
                "count": len(tokens)
            })
            
            print(f"📊 Saved trending tokens: {tokens}")
            
        except Exception as e:
            print(f"Error fetching and saving trending tokens: {e}")
    
    async def get_trending_tokens_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get trending tokens history for the last N hours"""
        try:
            collection = await get_collection(self.collection_name)
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Query recent records
            cursor = collection.find(
                {"timestamp": {"$gte": cutoff_time.isoformat()}},
                sort=[("timestamp", -1)]
            )
            
            history = []
            async for record in cursor:
                history.append({
                    "tokens": record.get("tokens", []),
                    "timestamp": record.get("timestamp"),
                    "count": record.get("count", 0)
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting trending tokens history: {e}")
            return []
    
    async def get_most_trending_tokens(self, hours: int = 24) -> Dict[str, int]:
        """Get most frequently trending tokens in the last N hours"""
        try:
            history = await self.get_trending_tokens_history(hours)
            
            # Count token frequency
            token_counts = {}
            for record in history:
                for token in record.get("tokens", []):
                    token_counts[token] = token_counts.get(token, 0) + 1
            
            # Sort by frequency
            sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
            
            return dict(sorted_tokens[:10])  # Top 10
            
        except Exception as e:
            print(f"Error getting most trending tokens: {e}")
            return {}


# Global Twitter service instance
twitter_service = TwitterService() 