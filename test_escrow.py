"""
Test script for escrow deposit system
"""

import asyncio
import httpx
import json


async def test_escrow_system():
    """Test the complete escrow deposit flow"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🏦 Testing Escrow Deposit System")
        print("=" * 50)
        
        # Step 1: Register a user
        print("\n1. Registering test user...")
        register_data = {
            "email": "escrow@example.com",
            "password": "testpassword123",
            "full_name": "Escrow Test User"
        }
        
        try:
            response = await client.post(f"{base_url}/api/auth/register", json=register_data)
            print(f"   Status: {response.status_code}")
            if response.status_code != 201:
                print(f"   ❌ Registration failed: {response.text}")
                return
            print(f"   ✅ User registered")
        except Exception as e:
            print(f"   ❌ Registration error: {e}")
            return
        
        # Step 2: Login and get token
        print("\n2. Logging in...")
        login_data = {
            "email": "escrow@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = await client.post(f"{base_url}/api/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   ❌ Login failed: {response.text}")
                return
            token_data = response.json()
            access_token = token_data['access_token']
            print(f"   ✅ Login successful")
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return
        
        # Set headers for authenticated requests
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 3: Create escrow deposit
        print("\n3. Creating escrow deposit...")
        deposit_data = {
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "amount": 0.5,
            "token_symbol": "ETH"
        }
        
        try:
            response = await client.post(f"{base_url}/api/escrow/deposits", json=deposit_data, headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                deposit_response = response.json()
                deposit_id = deposit_response['deposit_id']
                print(f"   ✅ Escrow deposit created: {deposit_response['message']}")
            else:
                print(f"   ❌ Escrow deposit failed: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Escrow deposit error: {e}")
            return
        
        # Step 4: Get escrow deposits
        print("\n4. Getting escrow deposits...")
        try:
            response = await client.get(f"{base_url}/api/escrow/deposits", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                deposits_response = response.json()
                print(f"   ✅ Found {deposits_response['count']} deposits")
                print(f"   📊 Total amount: {deposits_response['total_amount']}")
                print(f"   ⏳ Pending: {deposits_response['pending_count']}")
                print(f"   ✅ Confirmed: {deposits_response['confirmed_count']}")
            else:
                print(f"   ❌ Get deposits failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Get deposits error: {e}")
        
        # Step 5: Get escrow status
        print("\n5. Getting escrow status...")
        try:
            response = await client.get(f"{base_url}/api/escrow/status", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                status_response = response.json()
                print(f"   ✅ Escrow status retrieved")
                print(f"   🏦 Escrow wallet: {status_response['escrow_wallet']}")
                print(f"   📡 Listener status: {status_response['listener_status']}")
                print(f"   💰 Total deposits: {status_response['total_deposits']}")
                print(f"   💵 Total amount: {status_response['total_amount']}")
            else:
                print(f"   ❌ Get status failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Get status error: {e}")
        
        # Step 6: Get specific deposit
        print(f"\n6. Getting specific deposit {deposit_id}...")
        try:
            response = await client.get(f"{base_url}/api/escrow/deposits/{deposit_id}", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                deposit_detail = response.json()
                print(f"   ✅ Deposit details retrieved")
                print(f"   🪙 Amount: {deposit_detail['deposit']['amount']} {deposit_detail['deposit']['token_symbol']}")
                print(f"   📍 Status: {deposit_detail['deposit']['status']}")
                print(f"   👛 Wallet: {deposit_detail['deposit']['wallet_address']}")
            else:
                print(f"   ❌ Get deposit failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Get deposit error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Escrow deposit system test completed!")
        print("\n💡 Next steps:")
        print("   1. Send actual crypto to the escrow wallet address")
        print("   2. The blockchain listener will detect the transaction")
        print("   3. The deposit status will automatically update to 'confirmed'")


if __name__ == "__main__":
    asyncio.run(test_escrow_system()) 