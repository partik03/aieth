"""
Test script for dashboard API functionality
"""

import asyncio
import httpx
import json


async def test_dashboard_api():
    """Test the dashboard API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("📊 Testing Dashboard API")
        print("=" * 50)
        
        # Step 1: Register a test user
        print("\n1. Registering test user...")
        register_data = {
            "email": "dashboard@example.com",
            "password": "testpassword123",
            "full_name": "Dashboard Test User"
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
            "email": "dashboard@example.com",
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
        
        # Step 3: Test dashboard summary
        print("\n3. Testing dashboard summary...")
        try:
            response = await client.get(f"{base_url}/api/dashboard/summary", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                summary = response.json()
                print(f"   ✅ Dashboard summary retrieved")
                print(f"   💰 Wallet balances: {summary['data']['wallet_balances']}")
                print(f"   📊 Escrow activity: {summary['data']['escrow_activity']}")
                print(f"   📈 Investment performance: {summary['data']['investment_performance']}")
            else:
                print(f"   ❌ Dashboard summary failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Dashboard summary error: {e}")
        
        # Step 4: Test wallet balances
        print("\n4. Testing wallet balances...")
        try:
            response = await client.get(f"{base_url}/api/dashboard/balances", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                balances = response.json()
                print(f"   ✅ Wallet balances retrieved")
                print(f"   💵 Balances: {balances['data']['balances']}")
                print(f"   🪙 Total crypto value: {balances['data']['total_crypto_value']}")
            else:
                print(f"   ❌ Wallet balances failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Wallet balances error: {e}")
        
        # Step 5: Test recent transactions
        print("\n5. Testing recent transactions...")
        try:
            response = await client.get(f"{base_url}/api/dashboard/transactions?limit=5", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                transactions = response.json()
                print(f"   ✅ Recent transactions retrieved")
                print(f"   📝 Transaction count: {transactions['data']['count']}")
                for tx in transactions['data']['transactions'][:3]:  # Show first 3
                    print(f"      - {tx.get('type', 'unknown')}: {tx.get('amount', 0)}")
            else:
                print(f"   ❌ Recent transactions failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Recent transactions error: {e}")
        
        # Step 6: Test investment summary
        print("\n6. Testing investment summary...")
        try:
            response = await client.get(f"{base_url}/api/dashboard/investments", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                investments = response.json()
                print(f"   ✅ Investment summary retrieved")
                print(f"   📊 Performance: {investments['data']['performance']}")
                if investments['data']['last_investment']:
                    print(f"   💼 Last investment: {investments['data']['last_investment']['amount']} INR")
                else:
                    print(f"   💼 No investment history")
            else:
                print(f"   ❌ Investment summary failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Investment summary error: {e}")
        
        # Step 7: Test escrow summary
        print("\n7. Testing escrow summary...")
        try:
            response = await client.get(f"{base_url}/api/dashboard/escrow", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                escrow = response.json()
                print(f"   ✅ Escrow summary retrieved")
                print(f"   🏦 Escrow activity: {escrow['data']['escrow_activity']}")
                print(f"   📊 Net escrow: {escrow['data']['net_escrow']}")
            else:
                print(f"   ❌ Escrow summary failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Escrow summary error: {e}")
        
        # Step 8: Test analytics summary
        print("\n8. Testing analytics summary...")
        try:
            response = await client.get(f"{base_url}/api/dashboard/analytics", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                analytics = response.json()
                print(f"   ✅ Analytics summary retrieved")
                print(f"   📈 Portfolio value: {analytics['data']['total_portfolio_value']}")
                print(f"   🪙 Crypto allocation: {analytics['data']['crypto_allocation']:.1f}%")
                print(f"   💵 Fiat allocation: {analytics['data']['fiat_allocation']:.1f}%")
                print(f"   🏦 Escrow utilization: {analytics['data']['escrow_utilization']:.1f}%")
                print(f"   📊 Active tokens: {analytics['data']['active_tokens']}")
            else:
                print(f"   ❌ Analytics summary failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Analytics summary error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Dashboard API test completed!")
        print("\n💡 Dashboard endpoints available:")
        print("   - GET /api/dashboard/summary - Complete dashboard summary")
        print("   - GET /api/dashboard/balances - Wallet balances only")
        print("   - GET /api/dashboard/transactions - Recent transactions")
        print("   - GET /api/dashboard/investments - Investment summary")
        print("   - GET /api/dashboard/escrow - Escrow activity")
        print("   - GET /api/dashboard/analytics - Analytics and metrics")


if __name__ == "__main__":
    asyncio.run(test_dashboard_api()) 