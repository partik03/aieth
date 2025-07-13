"""
End-to-end test script for complete crypto deposit to UPI purchase flow
"""

import asyncio
import httpx
import json
import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import uuid

# Add the parent directory to the path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_DEPOSITOR_EMAIL = "depositor@test.com"
TEST_BUYER_EMAIL = "buyer@test.com"
TEST_PASSWORD = "testpassword123"


class FullFlowTester:
    """End-to-end flow tester for crypto deposit to UPI purchase"""
    
    def __init__(self):
        self.depositor_token = None
        self.buyer_token = None
        self.depositor_user_id = None
        self.buyer_user_id = None
        self.escrow_deposit_id = None
        self.upi_txn_ref = None
        
    async def run_full_test(self) -> Dict[str, Any]:
        """Run the complete end-to-end test flow"""
        print("🚀 Starting End-to-End Flow Test")
        print("=" * 60)
        
        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Create and authenticate users
                await self._step_1_create_users(client)
                
                # Step 2: Simulate crypto deposit
                escrow_result = await self._step_2_crypto_deposit(client)
                
                # Step 3: Simulate blockchain confirmation
                confirmation_result = await self._step_3_blockchain_confirmation()
                
                # Step 4: Buyer purchases via UPI
                purchase_result = await self._step_4_upi_purchase(client)
                
                # Step 5: Simulate UPI payment success
                upi_result = await self._step_5_upi_success(client)
                
                # Step 6: Verify crypto release
                release_result = await self._step_6_verify_release()
                
                # Step 7: Get dashboard summaries
                dashboard_result = await self._step_7_dashboard_summaries(client)
                
                # Step 8: Get notifications
                notification_result = await self._step_8_notifications(client)
                
                # Compile final result
                final_result = {
                    "test_timestamp": datetime.now(timezone.utc).isoformat(),
                    "escrow_created": escrow_result,
                    "escrow_confirmed": confirmation_result,
                    "upi_buy_initiated": purchase_result,
                    "upi_payment_success": upi_result,
                    "crypto_released": release_result,
                    "buyer_dashboard": dashboard_result.get("buyer"),
                    "depositor_dashboard": dashboard_result.get("depositor"),
                    "notifications": notification_result,
                    "test_summary": {
                        "total_steps": 8,
                        "successful_steps": sum([
                            1 if escrow_result else 0,
                            1 if confirmation_result else 0,
                            1 if purchase_result else 0,
                            1 if upi_result else 0,
                            1 if release_result else 0,
                            1 if dashboard_result else 0,
                            1 if notification_result else 0
                        ]),
                        "flow_completed": all([
                            escrow_result, confirmation_result, purchase_result,
                            upi_result, release_result, dashboard_result, notification_result
                        ])
                    }
                }
                
                print("\n" + "=" * 60)
                print("🎉 End-to-End Flow Test Completed!")
                print(f"✅ Success Rate: {final_result['test_summary']['successful_steps']}/{final_result['test_summary']['total_steps']}")
                print(f"🎯 Flow Completed: {final_result['test_summary']['flow_completed']}")
                
                return final_result
                
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                return {"error": str(e), "test_timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def _step_1_create_users(self, client: httpx.AsyncClient):
        """Step 1: Create and authenticate two users"""
        print("\n👤 Step 1: Creating and authenticating users...")
        
        # Create depositor (outside India)
        depositor_data = {
            "email": TEST_DEPOSITOR_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Crypto Depositor (International)"
        }
        
        response = await client.post(f"{BASE_URL}/api/auth/register", json=depositor_data)
        if response.status_code == 201:
            print("   ✅ Depositor registered")
        elif response.status_code == 400 and "already registered" in response.text:
            print("   ℹ️  Depositor already exists")
        else:
            print(f"   ❌ Depositor registration failed: {response.text}")
            return False
        
        # Create buyer (Indian user)
        buyer_data = {
            "email": TEST_BUYER_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "UPI Buyer (India)"
        }
        
        response = await client.post(f"{BASE_URL}/api/auth/register", json=buyer_data)
        if response.status_code == 201:
            print("   ✅ Buyer registered")
        elif response.status_code == 400 and "already registered" in response.text:
            print("   ℹ️  Buyer already exists")
        else:
            print(f"   ❌ Buyer registration failed: {response.text}")
            return False
        
        # Login both users
        login_data = {"email": TEST_DEPOSITOR_EMAIL, "password": TEST_PASSWORD}
        response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            self.depositor_token = response.json()["access_token"]
            print(f"   ✅ Depositor authenticated (token: {self.depositor_token[:20]}...)")
        else:
            print(f"   ❌ Depositor login failed: {response.text}")
            return False
        
        login_data = {"email": TEST_BUYER_EMAIL, "password": TEST_PASSWORD}
        response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            self.buyer_token = response.json()["access_token"]
            print(f"   ✅ Buyer authenticated (token: {self.buyer_token[:20]}...)")
        else:
            print(f"   ❌ Buyer login failed: {response.text}")
            return False
        
        # Get user IDs from database
        try:
            from src.services.auth import auth_service
            await auth_service.db.connect()
            
            depositor_user = await auth_service.get_user_by_email(TEST_DEPOSITOR_EMAIL)
            buyer_user = await auth_service.get_user_by_email(TEST_BUYER_EMAIL)
            
            if depositor_user:
                self.depositor_user_id = depositor_user.id
            if buyer_user:
                self.buyer_user_id = buyer_user.id
                
        except Exception as e:
            print(f"   ⚠️  Could not get user IDs: {e}")
            # Fallback to using emails
            self.depositor_user_id = TEST_DEPOSITOR_EMAIL
            self.buyer_user_id = TEST_BUYER_EMAIL
        
        print("   ✅ Both users created and authenticated")
        return True
    
    async def _step_2_crypto_deposit(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Step 2: Simulate crypto deposit via escrow"""
        print("\n💰 Step 2: Simulating crypto deposit...")
        
        # Create escrow deposit
        deposit_data = {
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "amount": 0.5,
            "token_symbol": "ETH"
        }
        
        headers = {"Authorization": f"Bearer {self.depositor_token}"}
        response = await client.post(f"{BASE_URL}/api/escrow/deposits", json=deposit_data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            self.escrow_deposit_id = result["deposit_id"]
            print(f"   ✅ Escrow deposit created: {result['message']}")
            return result
        else:
            print(f"   ❌ Escrow deposit failed: {response.text}")
            return None
    
    async def _step_3_blockchain_confirmation(self) -> bool:
        """Step 3: Simulate blockchain confirmation"""
        print("\n🔗 Step 3: Simulating blockchain confirmation...")
        
        # Import the mock blockchain listener to simulate confirmation
        from src.services.mock_blockchain_listener import mock_blockchain_listener
        
        try:
            # Get the escrow deposit
            escrow_deposits = await mock_blockchain_listener.get_escrow_deposits()
            target_deposit = None
            
            for deposit in escrow_deposits:
                if deposit.get("_id") == self.escrow_deposit_id:
                    target_deposit = deposit
                    break
            
            if target_deposit:
                # Simulate confirmation
                await mock_blockchain_listener._confirm_deposit(target_deposit)
                print("   ✅ Escrow deposit confirmed on blockchain")
                return True
            else:
                print("   ❌ Escrow deposit not found for confirmation")
                return False
                
        except Exception as e:
            print(f"   ❌ Blockchain confirmation failed: {e}")
            return False
    
    async def _step_4_upi_purchase(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Step 4: Buyer purchases crypto via UPI"""
        print("\n🛒 Step 4: Buyer purchasing crypto via UPI...")
        
        # Buyer initiates purchase
        buy_data = {
            "user_id": self.buyer_user_id,
            "crypto_type": "ETH",
            "amount": 0.3  # Buy less than deposited
        }
        
        headers = {"Authorization": f"Bearer {self.buyer_token}"}
        response = await client.post(f"{BASE_URL}/api/escrow/buy", json=buy_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            self.upi_txn_ref = result["txn_ref"]
            print(f"   ✅ UPI purchase initiated: {result['message']}")
            print(f"   📱 UPI String: {result['upi_string']}")
            return result
        else:
            print(f"   ❌ UPI purchase failed: {response.text}")
            return None
    
    async def _step_5_upi_success(self, client: httpx.AsyncClient) -> bool:
        """Step 5: Simulate UPI payment success"""
        print("\n💳 Step 5: Simulating UPI payment success...")
        
        if not self.upi_txn_ref:
            print("   ❌ No UPI transaction reference available")
            return False
        
        # Simulate UPI callback with success
        callback_data = {
            "txn_ref": self.upi_txn_ref,
            "status": "success"
        }
        
        response = await client.post(f"{BASE_URL}/api/upi/mock-callback", json=callback_data)
        
        if response.status_code == 200:
            print("   ✅ UPI payment processed successfully")
            return True
        else:
            print(f"   ❌ UPI payment failed: {response.text}")
            return False
    
    async def _step_6_verify_release(self) -> bool:
        """Step 6: Verify crypto has been released"""
        print("\n🔓 Step 6: Verifying crypto release...")
        
        try:
            from src.services.mock_blockchain_listener import mock_blockchain_listener
            
            # Check escrow status
            escrow_deposits = await mock_blockchain_listener.get_escrow_deposits()
            
            for deposit in escrow_deposits:
                if deposit.get("_id") == self.escrow_deposit_id:
                    status = deposit.get("status")
                    if status == "released":
                        print("   ✅ Crypto successfully released to buyer")
                        return True
                    else:
                        print(f"   ❌ Escrow status is {status}, expected 'released'")
                        return False
            
            print("   ❌ Escrow deposit not found")
            return False
            
        except Exception as e:
            print(f"   ❌ Verification failed: {e}")
            return False
    
    async def _step_7_dashboard_summaries(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Step 7: Get dashboard summaries for both users"""
        print("\n📊 Step 7: Fetching dashboard summaries...")
        
        result = {}
        
        # Get depositor dashboard
        headers = {"Authorization": f"Bearer {self.depositor_token}"}
        response = await client.get(f"{BASE_URL}/api/dashboard/summary", headers=headers)
        if response.status_code == 200:
            result["depositor"] = response.json()["data"]
            print("   ✅ Depositor dashboard retrieved")
        else:
            print(f"   ❌ Depositor dashboard failed: {response.text}")
        
        # Get buyer dashboard
        headers = {"Authorization": f"Bearer {self.buyer_token}"}
        response = await client.get(f"{BASE_URL}/api/dashboard/summary", headers=headers)
        if response.status_code == 200:
            result["buyer"] = response.json()["data"]
            print("   ✅ Buyer dashboard retrieved")
        else:
            print(f"   ❌ Buyer dashboard failed: {response.text}")
        
        return result
    
    async def _step_8_notifications(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Step 8: Get notifications for both users"""
        print("\n🔔 Step 8: Fetching notifications...")
        
        result = {"buyer": [], "depositor": []}
        
        # Try to get notifications (if notification endpoint exists)
        try:
            headers = {"Authorization": f"Bearer {self.depositor_token}"}
            response = await client.get(f"{BASE_URL}/api/notifications", headers=headers)
            if response.status_code == 200:
                result["depositor"] = response.json().get("notifications", [])
                print("   ✅ Depositor notifications retrieved")
            else:
                print("   ℹ️  No notification endpoint found for depositor")
        except:
            print("   ℹ️  Notification endpoint not available")
        
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = await client.get(f"{BASE_URL}/api/notifications", headers=headers)
            if response.status_code == 200:
                result["buyer"] = response.json().get("notifications", [])
                print("   ✅ Buyer notifications retrieved")
            else:
                print("   ℹ️  No notification endpoint found for buyer")
        except:
            print("   ℹ️  Notification endpoint not available")
        
        return result


async def run_full_flow_test():
    """Main function to run the full flow test"""
    tester = FullFlowTester()
    result = await tester.run_full_test()
    
    # Save result to file
    with open("test_results_full_flow.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to: test_results_full_flow.json")
    
    return result


if __name__ == "__main__":
    asyncio.run(run_full_flow_test()) 