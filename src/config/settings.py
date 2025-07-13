"""
Application settings and configuration management
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    mongo_uri: str = Field(..., env="MONGO_URI")
    db_name: str = Field(..., env="DB_NAME")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    upi_gateway_api_key: str = Field(..., env="UPI_GATEWAY_API_KEY")
    upi_gateway_secret: str = Field(..., env="UPI_GATEWAY_SECRET")
    
    # Blockchain
    ethereum_rpc_url: str = Field(..., env="ETHEREUM_RPC_URL")
    polygon_rpc_url: str = Field(..., env="POLYGON_RPC_URL")
    private_key: str = Field(..., env="PRIVATE_KEY")
    
    # External APIs
    crypto_price_api_url: str = Field(default="https://api.coingecko.com/api/v3", env="CRYPTO_PRICE_API_URL")
    twitter_api_key: str = Field(..., env="TWITTER_API_KEY")
    twitter_api_secret: str = Field(..., env="TWITTER_API_SECRET")
    
    # Application
    debug: bool = Field(default=True, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # UPI
    upi_merchant_id: str = Field(..., env="UPI_MERCHANT_ID")
    upi_app_id: str = Field(..., env="UPI_APP_ID")
    upi_callback_url: str = Field(..., env="UPI_CALLBACK_URL")
    
    # DigiLocker
    digilocker_client_id: str = Field(..., env="DIGILOCKER_CLIENT_ID")
    digilocker_client_secret: str = Field(..., env="DIGILOCKER_CLIENT_SECRET")
    digilocker_redirect_uri: str = Field(..., env="DIGILOCKER_REDIRECT_URI")
    digilocker_base_url: str = Field(..., env="DIGILOCKER_BASE_URL")
    
    # AI
    ai_model: str = Field(default="gpt-4", env="AI_MODEL")
    ai_max_tokens: int = Field(default=1000, env="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.7, env="AI_TEMPERATURE")

    # Azure OpenAI
    azure_openai_endpoint: str = Field(default="https://jaggery-open-ai.openai.azure.com/openai/deployments/gpt-4.1-2/chat/completions?api-version=2025-01-01-preview", env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(default="5NwK8dktlJQ5ZPNBHjoBDVcgNdLASKJEF3MFCN5MfnUpKe3K2AY8JQQJ99ALACYeBjFXJ3w3AAABACOGc4FA", env="AZURE_OPENAI_API_KEY")
    azure_openai_deployment: str = Field(default="gpt-4.1-2", env="AZURE_OPENAI_DEPLOYMENT")
    
    # Escrow
    escrow_wallet_address: str = Field(..., env="ESCROW_WALLET_ADDRESS")
    escrow_private_key: str = Field(..., env="ESCROW_PRIVATE_KEY")
    
    # Microfinance
    loan_interest_rate: float = Field(default=0.12, env="LOAN_INTEREST_RATE")
    max_loan_amount: float = Field(default=100000, env="MAX_LOAN_AMOUNT")
    min_credit_score: int = Field(default=600, env="MIN_CREDIT_SCORE")
    
    # Biconomy Smart Account
    biconomy_api_key: str = Field(..., env="BICONOMY_API_KEY")
    biconomy_relayer_key: str = Field(..., env="BICONOMY_RELAYER_KEY")
    chain_id: int = Field(default=80001, env="CHAIN_ID")  # Mumbai testnet
    entry_point_address: str = Field(default="0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789", env="ENTRY_POINT_ADDRESS")
    web3_rpc_url: str = Field(..., env="WEB3_RPC_URL")
    sepolia_rpc_url: str = Field(..., env="SEPOLIA_RPC_URL")
    etherscan_api_key: str = Field(..., env="ETHERSCAN_API_KEY")

    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 