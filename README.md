# Crypto-UPI Backend

A FastAPI backend for a 20-hour hackathon project combining AI, Web3, and UPI to enable crypto trading in India.

## Features

- **UPI Integration**: Indian users can buy crypto using UPI payments
- **Escrow System**: International users can deposit crypto for Indian buyers
- **Wallet System**: Dual crypto and INR balance management
- **AI Agent**: Automated investment strategies and natural language wallet commands
- **QR Code Payments**: UPI payments backed by deposited crypto
- **Microfinance**: Optional loan features with AI risk scoring

## Project Structure

```
backend/
├── src/                    # Main application code
│   ├── api/               # FastAPI route definitions
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── crypto.py      # Crypto trading endpoints
│   │   ├── escrow.py      # Escrow management endpoints
│   │   ├── upi.py         # UPI payment endpoints
│   │   ├── wallet.py      # Wallet management endpoints
│   │   ├── ai_agent.py    # AI agent endpoints
│   │   └── microfinance.py # Loan and risk scoring endpoints
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── crypto_service.py    # Crypto trading logic
│   │   ├── escrow_service.py    # Escrow wallet management
│   │   ├── upi_service.py       # UPI payment processing
│   │   ├── wallet_service.py    # Wallet operations
│   │   ├── ai_agent_service.py  # AI investment strategies
│   │   ├── risk_scoring.py      # AI risk assessment
│   │   └── blockchain_service.py # Web3 interactions
│   ├── models/            # Database models
│   │   ├── __init__.py
│   │   ├── user.py        # User model
│   │   ├── wallet.py      # Wallet model
│   │   ├── transaction.py # Transaction model
│   │   ├── escrow.py      # Escrow model
│   │   └── loan.py        # Loan model
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   ├── qr_generator.py      # QR code generation
│   │   ├── nlp_parser.py        # Natural language processing
│   │   ├── crypto_utils.py      # Crypto-related utilities
│   │   ├── upi_utils.py         # UPI payment utilities
│   │   └── validators.py        # Input validation
│   └── config/            # Configuration
│       ├── __init__.py
│       ├── settings.py    # Environment settings
│       ├── database.py    # Database configuration
│       └── constants.py   # Application constants
├── scripts/               # One-time scripts
│   ├── init_db.py         # Database initialization
│   ├── seed_data.py       # Sample data seeding
│   └── test_setup.py      # Test environment setup
├── tests/                 # Test files
│   ├── __init__.py
│   ├── test_api/          # API endpoint tests
│   ├── test_services/     # Service layer tests
│   └── test_utils/        # Utility function tests
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── main.py               # FastAPI application entry point
```

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database setup**:
   ```bash
   python scripts/init_db.py
   ```

4. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

- **Run tests**: `pytest`
- **Format code**: `black src/ tests/`
- **Lint code**: `flake8 src/ tests/`

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Authentication**: JWT tokens
- **Crypto**: Web3.py for blockchain interactions
- **AI**: OpenAI API for natural language processing
- **UPI**: Integration with payment gateways
- **QR Codes**: qrcode library
- **Testing**: pytest

## Hackathon Timeline

- **Hour 1-2**: Project setup and basic structure
- **Hour 3-4**: Database models and basic API endpoints
- **Hour 5-6**: UPI integration and payment processing
- **Hour 7-8**: Crypto wallet and escrow system
- **Hour 9-10**: AI agent for investment strategies
- **Hour 11-12**: Natural language processing for wallet commands
- **Hour 13-14**: QR code generation and payment flows
- **Hour 15-16**: Microfinance features and risk scoring
- **Hour 17-18**: Testing and bug fixes
- **Hour 19-20**: Documentation and deployment preparation 