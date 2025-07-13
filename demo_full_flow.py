"""
Demo script for the full end-to-end flow test
"""

import asyncio
import json
from datetime import datetime


async def run_demo():
    """Run the full flow demo"""
    print("🎬 Crypto + UPI + AI Platform - Full Flow Demo")
    print("=" * 60)
    print("This demo simulates the complete flow from crypto deposit to UPI purchase")
    print("and crypto release, showcasing our trustless escrow system.")
    print()
    
    try:
        # Import and run the full flow test
        from scripts.test_full_flow import run_full_flow_test
        
        print("🚀 Starting the demo...")
        print()
        
        # Run the test
        result = await run_full_flow_test()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 DEMO RESULTS")
        print("=" * 60)
        
        if "error" in result:
            print(f"❌ Demo failed: {result['error']}")
            return
        
        # Test summary
        summary = result.get("test_summary", {})
        print(f"✅ Success Rate: {summary.get('successful_steps', 0)}/{summary.get('total_steps', 0)}")
        print(f"🎯 Flow Completed: {summary.get('flow_completed', False)}")
        print()
        
        # Escrow flow
        if result.get("escrow_created"):
            escrow = result["escrow_created"]
            print("💰 ESCROW DEPOSIT")
            print(f"   Amount: {escrow.get('deposit', {}).get('amount', 0)} {escrow.get('deposit', {}).get('token_symbol', 'ETH')}")
            print(f"   Status: {escrow.get('deposit', {}).get('status', 'pending')}")
            print(f"   Message: {escrow.get('message', '')}")
            print()
        
        if result.get("escrow_confirmed"):
            print("🔗 BLOCKCHAIN CONFIRMATION")
            print("   ✅ Deposit confirmed on blockchain")
            print("   ✅ Escrow status updated to 'confirmed'")
            print()
        
        if result.get("upi_buy_initiated"):
            upi = result["upi_buy_initiated"]
            print("🛒 UPI PURCHASE INITIATED")
            print(f"   Amount: {upi.get('amount', 0)} {upi.get('crypto_type', 'ETH')}")
            print(f"   UPI String: {upi.get('upi_string', '')}")
            print(f"   Transaction Ref: {upi.get('txn_ref', '')}")
            print()
        
        if result.get("upi_payment_success"):
            print("💳 UPI PAYMENT SUCCESS")
            print("   ✅ Payment processed successfully")
            print("   ✅ Escrow marked as 'pending_upi'")
            print()
        
        if result.get("crypto_released"):
            print("🔓 CRYPTO RELEASE")
            print("   ✅ Crypto successfully transferred to buyer")
            print("   ✅ Escrow status updated to 'released'")
            print("   ✅ Wallet balances updated")
            print()
        
        # Dashboard summaries
        if result.get("buyer_dashboard"):
            buyer = result["buyer_dashboard"]
            print("📊 BUYER DASHBOARD")
            print(f"   Wallet Balances: {buyer.get('wallet_balances', {})}")
            print(f"   Escrow Activity: {buyer.get('escrow_activity', {})}")
            print()
        
        if result.get("depositor_dashboard"):
            depositor = result["depositor_dashboard"]
            print("📊 DEPOSITOR DASHBOARD")
            print(f"   Wallet Balances: {depositor.get('wallet_balances', {})}")
            print(f"   Escrow Activity: {depositor.get('escrow_activity', {})}")
            print()
        
        # Notifications
        notifications = result.get("notifications", {})
        if notifications.get("buyer") or notifications.get("depositor"):
            print("🔔 NOTIFICATIONS")
            if notifications.get("buyer"):
                print(f"   Buyer: {len(notifications['buyer'])} notifications")
            if notifications.get("depositor"):
                print(f"   Depositor: {len(notifications['depositor'])} notifications")
            print()
        
        print("=" * 60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("💡 Key Features Demonstrated:")
        print("   • JWT Authentication for both users")
        print("   • Crypto deposit via escrow system")
        print("   • Real-time blockchain confirmation")
        print("   • UPI payment integration")
        print("   • Automated crypto release")
        print("   • Dashboard analytics")
        print("   • End-to-end transaction tracking")
        print()
        print("🚀 This demonstrates a complete trustless crypto + UPI platform!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure the server is running and all services are active.")


if __name__ == "__main__":
    asyncio.run(run_demo()) 