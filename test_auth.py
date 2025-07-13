"""
Test script for authentication system
"""

import asyncio
import httpx
import json


async def test_auth_system():
    """Test the complete authentication flow"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🔐 Testing Authentication System")
        print("=" * 50)
        
        # Test 1: Register a new user
        print("\n1. Testing user registration...")
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        try:
            response = await client.post(f"{base_url}/api/auth/register", json=register_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                user_data = response.json()
                print(f"   ✅ User registered: {user_data['email']}")
                user_id = user_data['id']
            else:
                print(f"   ❌ Registration failed: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Registration error: {e}")
            return
        
        # Test 2: Login with the registered user
        print("\n2. Testing user login...")
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = await client.post(f"{base_url}/api/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data['access_token']
                print(f"   ✅ Login successful, token received")
            else:
                print(f"   ❌ Login failed: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return
        
        # Test 3: Get current user info with token
        print("\n3. Testing token verification...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = await client.get(f"{base_url}/api/auth/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ Token verified: {user_info['email']}")
            else:
                print(f"   ❌ Token verification failed: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Token verification error: {e}")
            return
        
        # Test 4: Test protected endpoint (salary)
        print("\n4. Testing protected endpoint...")
        salary_data = {
            "amount": 50000,
            "employer": "Test Company",
            "date": "2024-01-15"
        }
        
        try:
            response = await client.post(f"{base_url}/api/salary", json=salary_data, headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                salary_response = response.json()
                print(f"   ✅ Protected endpoint accessed: {salary_response['message']}")
            else:
                print(f"   ❌ Protected endpoint failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Protected endpoint error: {e}")
        
        # Test 5: Test unauthorized access
        print("\n5. Testing unauthorized access...")
        try:
            response = await client.post(f"{base_url}/api/salary", json=salary_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 401:
                print(f"   ✅ Unauthorized access properly blocked")
            else:
                print(f"   ❌ Unauthorized access not blocked: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Unauthorized test error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Authentication system test completed!")


if __name__ == "__main__":
    asyncio.run(test_auth_system()) 