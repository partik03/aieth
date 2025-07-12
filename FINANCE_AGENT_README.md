# Finance Agent with Azure OpenAI Integration

## Overview

This project now includes a comprehensive Finance Agent that uses Azure OpenAI to analyze UPI transaction data and provide intelligent financial insights and recommendations. The system generates realistic mock UPI transaction data and uses AI to provide personalized financial advice.

## Features

### 🤖 AI-Powered Financial Analysis
- **Transaction Analysis**: Deep analysis of spending patterns using Azure OpenAI
- **Financial Insights**: Personalized recommendations based on transaction history
- **Spending Pattern Recognition**: Identifies trends and anomalies in spending behavior
- **Risk Assessment**: Evaluates financial health and potential risks

### 📊 Mock UPI Data Generation
- **Realistic Transaction Data**: Generates authentic UPI transaction records
- **Multiple Categories**: Food & Dining, Shopping, Transportation, Entertainment, etc.
- **Time-based Analysis**: Supports different time periods (30, 60, 90 days)
- **Category Filtering**: Filter transactions by spending categories
- **Date Range Filtering**: Analyze specific time periods

### 💬 Natural Language Interface
- **Conversational AI**: Chat with the finance agent using natural language
- **Intent Recognition**: Automatically detects user intent from messages
- **Contextual Responses**: Provides relevant financial advice based on user queries

## Architecture

### Core Components

1. **FinanceAgentService** (`src/services/finance_agent.py`)
   - Azure OpenAI integration
   - Transaction analysis and insights generation
   - Financial recommendations engine

2. **MockUPIDataService** (`src/services/mock_upi_data.py`)
   - Mock UPI transaction generation
   - Transaction categorization and filtering
   - Data export and summary generation

3. **Enhanced NLPService** (`src/services/nlp_service.py`)
   - Natural language processing for financial queries
   - Intent detection for financial analysis commands
   - Integration with finance agent and mock data

### Azure OpenAI Configuration

The system is configured to use Azure OpenAI with the following settings:

```python
# Azure OpenAI Configuration
azure_openai_endpoint: "https://jaggery-open-ai.openai.azure.com/openai/deployments/gpt-4.1-2/chat/completions?api-version=2025-01-01-preview"
azure_openai_api_key: "5NwK8dktlJQ5ZPNBHjoBDVcgNdLASKJEF3MFCN5MfnUpKe3K2AY8JQQJ99ALACYeBjFXJ3w3AAABACOGc4FA"
azure_openai_deployment: "gpt-4.1-2"
```

## Usage

### WebSocket Chat Interface

Connect to the WebSocket endpoint and use natural language commands:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat/user123');

// Send financial analysis requests
ws.send(JSON.stringify({
    message: "analyze my transactions"
}));

ws.send(JSON.stringify({
    message: "give me financial insights"
}));

ws.send(JSON.stringify({
    message: "show me transaction summary"
}));
```

### Available Commands

#### 📊 Financial Analysis Commands
- `"analyze my transactions"` - Deep transaction analysis with AI insights
- `"financial insights"` - Get personalized financial advice
- `"transaction summary"` - Monthly spending summary
- `"spending analysis"` - Detailed spending pattern analysis

#### 💸 Traditional Wallet Commands
- `"send 1000 to Alice"` - Transfer money
- `"check balance"` - View wallet balance
- `"invest salary 50000"` - Investment strategy

### API Endpoints

The system integrates with the existing WebSocket chat API:

- **WebSocket Endpoint**: `/ws/chat/{user_id}`
- **Message Format**: JSON with `message` field
- **Response Format**: Structured JSON with analysis results

## Mock Data Structure

### Transaction Categories
- **Food & Dining**: Swiggy, Zomato, Domino's, etc.
- **Shopping**: Amazon, Flipkart, Myntra, etc.
- **Transportation**: Uber, Ola, Metro, etc.
- **Entertainment**: Netflix, Amazon Prime, BookMyShow, etc.
- **Utilities**: BSES, Airtel, Jio, etc.
- **Healthcare**: Apollo Pharmacy, MedPlus, etc.
- **Education**: Coursera, Udemy, BYJU'S, etc.
- **Finance**: HDFC Bank, ICICI Bank, Paytm, etc.
- **Travel**: Booking.com, Airbnb, Goibibo, etc.

### Transaction Data Fields
```json
{
    "transaction_id": "TXN123456",
    "user_id": "user123",
    "date": "2024-01-15T10:30:00",
    "amount": 1500.00,
    "transaction_type": "DEBIT",
    "category": "Food & Dining",
    "merchant": "Swiggy",
    "upi_id": "user123@okicici",
    "reference_number": "REF123456789",
    "status": "SUCCESS",
    "remarks": "Payment to Swiggy"
}
```

## Testing

### Run the Test Suite

```bash
# Install dependencies
pip install -r requirements.txt

# Run the finance agent test
python test_finance_agent.py
```

### Test Features

The test suite covers:
1. **Mock Data Generation**: Creates realistic UPI transactions
2. **AI Analysis**: Tests Azure OpenAI integration
3. **Financial Recommendations**: Validates recommendation generation
4. **NLP Integration**: Tests natural language processing
5. **Data Export**: Validates JSON export functionality
6. **Category Filtering**: Tests transaction filtering by category
7. **Date Range Filtering**: Tests time-based filtering

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://jaggery-open-ai.openai.azure.com/openai/deployments/gpt-4.1-2/chat/completions?api-version=2025-01-01-preview
AZURE_OPENAI_API_KEY=5NwK8dktlJQ5ZPNBHjoBDVcgNdLASKJEF3MFCN5MfnUpKe3K2AY8JQQJ99ALACYeBjFXJ3w3AAABACOGc4FA
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-2
```

### Dependencies

The system requires these additional dependencies:
- `aiohttp==3.9.1` - For Azure OpenAI API calls

## AI Analysis Features

### Spending Pattern Analysis
- Identifies spending trends and patterns
- Categorizes transactions by merchant and category
- Calculates spending ratios and percentages
- Detects unusual spending behavior

### Financial Health Assessment
- Evaluates overall financial health
- Identifies potential financial risks
- Suggests areas for improvement
- Provides credit score insights

### Savings Opportunities
- Identifies potential savings areas
- Suggests budget optimizations
- Recommends spending cuts
- Proposes investment opportunities

### Personalized Recommendations
- Immediate actions (next 7 days)
- Short-term goals (next 30 days)
- Medium-term planning (next 3 months)
- Long-term strategy (next 6-12 months)
- Investment opportunities
- Risk mitigation strategies

## Error Handling

The system includes comprehensive error handling:

- **Azure OpenAI API Failures**: Fallback to basic analysis
- **Network Issues**: Graceful degradation with cached responses
- **Invalid Data**: Validation and sanitization of transaction data
- **Rate Limiting**: Respects API rate limits with retry logic

## Security Considerations

- **API Key Protection**: Azure OpenAI keys are stored securely
- **Data Privacy**: Mock data doesn't contain real user information
- **Input Validation**: All user inputs are validated and sanitized
- **Error Logging**: Sensitive information is not logged

## Future Enhancements

### Planned Features
- **Real UPI Integration**: Connect to actual UPI transaction APIs
- **Machine Learning Models**: Custom ML models for better predictions
- **Budget Tracking**: Automated budget creation and monitoring
- **Investment Portfolio**: Crypto and traditional investment tracking
- **Financial Goals**: Goal setting and progress tracking
- **Expense Alerts**: Smart notifications for unusual spending

### Integration Opportunities
- **Bank APIs**: Direct bank account integration
- **Credit Score APIs**: Real-time credit score monitoring
- **Investment Platforms**: Integration with investment platforms
- **Tax Calculation**: Automated tax calculations and filing

## Support

For issues or questions:
1. Check the test suite for examples
2. Review the configuration settings
3. Verify Azure OpenAI API access
4. Check network connectivity

## License

This project is part of the AI-powered wallet assistant system. 