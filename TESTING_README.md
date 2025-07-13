# 🧪 Testing System for Crypto + UPI + AI Platform

This document describes the comprehensive testing system for our end-to-end crypto platform.

## 🎯 Overview

The testing system simulates the complete flow from crypto deposit to UPI purchase and crypto release, demonstrating our trustless escrow system.

## 📁 Test Files

### Core Test Scripts
- `scripts/test_full_flow.py` - Main end-to-end test script
- `demo_full_flow.py` - Demo script with formatted output
- `test_auth.py` - Authentication system tests
- `test_escrow.py` - Escrow system tests
- `test_dashboard.py` - Dashboard API tests

### Test Data
- `populate_test_data.py` - Populate test data for dashboard testing

## 🚀 Quick Start

### 1. Start the Server
```bash
# Start the FastAPI server with environment variables
MONGO_URI=mongodb://localhost:27017 DB_NAME=crypto_upi_db SECRET_KEY=dev-secret-key \
OPENAI_API_KEY=mock-key UPI_GATEWAY_API_KEY=mock-key UPI_GATEWAY_SECRET=mock-secret \
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/mock POLYGON_RPC_URL=https://polygon-rpc.com \
PRIVATE_KEY=mock-key TWITTER_API_KEY=mock-key TWITTER_API_SECRET=mock-secret \
UPI_MERCHANT_ID=mock-id UPI_APP_ID=mock-app UPI_CALLBACK_URL=http://localhost:8000/callback \
DIGILOCKER_CLIENT_ID=mock-id DIGILOCKER_CLIENT_SECRET=mock-secret \
DIGILOCKER_REDIRECT_URI=http://localhost:8000/callback \
DIGILOCKER_BASE_URL=https://api.digitallocker.gov.in/kyc \
ESCROW_WALLET_ADDRESS=0x1234567890123456789012345678901234567890 \
ESCROW_PRIVATE_KEY=mock-key python run.py
```

### 2. Run the Full Flow Demo
```bash
python demo_full_flow.py
```

### 3. Run Individual Tests
```bash
# Test authentication
python test_auth.py

# Test escrow system
python test_escrow.py

# Test dashboard
python test_dashboard.py

# Populate test data
python populate_test_data.py
```

## 🔄 End-to-End Flow Test

The full flow test simulates the complete user journey:

### Step 1: User Creation
- Creates two test users: `depositor@test.com` (international) and `buyer@test.com` (Indian)
- Authenticates both users with JWT tokens

### Step 2: Crypto Deposit
- Depositor creates escrow deposit (0.5 ETH)
- System generates escrow wallet address for deposit

### Step 3: Blockchain Confirmation
- Simulates blockchain confirmation of the deposit
- Updates escrow status to "confirmed"

### Step 4: UPI Purchase
- Buyer initiates purchase (0.3 ETH) via UPI
- System generates UPI string and QR code
- Escrow status becomes "pending_upi"

### Step 5: UPI Payment Success
- Simulates successful UPI payment
- Triggers escrow release process

### Step 6: Crypto Release
- Verifies crypto transfer from escrow to buyer
- Updates wallet balances
- Escrow status becomes "released"

### Step 7: Dashboard Summaries
- Fetches dashboard data for both users
- Shows wallet balances, escrow activity, transactions

### Step 8: Notifications
- Retrieves notifications for both users (if available)

## 📊 Test Results

The test generates a comprehensive JSON report:

```json
{
  "test_timestamp": "2024-01-15T10:30:00Z",
  "escrow_created": {
    "deposit_id": "escrow_123",
    "message": "Escrow deposit created. Send 0.5 ETH to 0x1234...",
    "deposit": {...}
  },
  "escrow_confirmed": true,
  "upi_buy_initiated": {
    "upi_string": "upi://pay?pa=test@upi&pn=Crypto&am=0.3",
    "qr_code": "base64_encoded_qr",
    "txn_ref": "TXN_ABC123"
  },
  "upi_payment_success": true,
  "crypto_released": true,
  "buyer_dashboard": {
    "wallet_balances": {"INR": 5000, "ETH": 0.3},
    "escrow_activity": {"purchased": 0.3}
  },
  "depositor_dashboard": {
    "wallet_balances": {"INR": 0, "ETH": 0.2},
    "escrow_activity": {"deposited": 0.5, "purchased": 0}
  },
  "notifications": {
    "buyer": [...],
    "depositor": [...]
  },
  "test_summary": {
    "total_steps": 8,
    "successful_steps": 8,
    "flow_completed": true
  }
}
```

## 🌐 API Testing Endpoints

### Test API Routes
- `GET /api/test/full-flow` - Run full flow test via HTTP
- `GET /api/test/health` - Health check
- `POST /api/test/reset-test-data` - Reset test data
- `GET /api/test/system-status` - System status

### Usage
```bash
# Run full flow test via API (requires authentication)
curl -X GET "http://localhost:8000/api/test/full-flow" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Health check
curl -X GET "http://localhost:8000/api/test/health"

# System status
curl -X GET "http://localhost:8000/api/test/system-status"
```

## 🧹 Test Data Management

### Reset Test Data
```bash
# Via API
curl -X POST "http://localhost:8000/api/test/reset-test-data" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Or manually clear collections
python -c "
from src.services.db import db_service
import asyncio

async def clear_test_data():
    await db_service.connect()
    collections = ['users', 'escrow_deposits', 'upi_payments', 'wallets']
    for collection in collections:
        await db_service.delete_documents(collection, {'email': {'$regex': '.*@test\\.com'}})
    print('Test data cleared')

asyncio.run(clear_test_data())
"
```

### Populate Test Data
```bash
python populate_test_data.py
```

## 🔧 Configuration

### Test Configuration
Edit `scripts/test_full_flow.py` to modify:
- Test user emails and passwords
- Crypto amounts and types
- Base URL for API calls

### Environment Variables
Ensure these are set for testing:
- `MONGO_URI` - MongoDB connection string
- `SECRET_KEY` - JWT secret key
- `ESCROW_WALLET_ADDRESS` - Escrow wallet address

## 📈 Monitoring

### Test Metrics
- Success rate per step
- Total flow completion
- Response times
- Error tracking

### Logs
- Test execution logs
- API response logs
- Error logs with stack traces

## 🐛 Troubleshooting

### Common Issues

1. **Server not running**
   ```bash
   # Check if server is running
   curl http://localhost:8000/ping
   ```

2. **Database connection issues**
   ```bash
   # Check MongoDB connection
   curl http://localhost:8000/api/test/health
   ```

3. **Authentication errors**
   ```bash
   # Check JWT token
   curl -X GET "http://localhost:8000/api/auth/me" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **Test data issues**
   ```bash
   # Reset test data
   python -c "from populate_test_data import populate_test_data; import asyncio; asyncio.run(populate_test_data())"
   ```

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=true
python demo_full_flow.py
```

## 🎯 Demo Scenarios

### Scenario 1: Basic Flow
- Single crypto deposit and purchase
- Demonstrates core escrow functionality

### Scenario 2: Multiple Transactions
- Multiple deposits and purchases
- Shows system scalability

### Scenario 3: Error Handling
- Failed payments and recoveries
- Demonstrates error resilience

## 📝 Test Reports

Test results are automatically saved to:
- `test_results_full_flow.json` - Full test results
- Console output with formatted results
- Optional database logging

## 🚀 Next Steps

1. **Add more test scenarios**
2. **Implement performance testing**
3. **Add integration with real blockchain**
4. **Create automated CI/CD pipeline**
5. **Add load testing**

---

This testing system provides comprehensive coverage of our crypto + UPI + AI platform, ensuring reliability and demonstrating the complete user journey from deposit to purchase. 