import { BiconomySmartAccountV2, BiconomySmartAccountV2Config } from '@biconomy/account'
import { ethers } from 'ethers'
import { ChainId } from '@biconomy/core-types'
import { Address } from 'abitype'

export interface BiconomyConfig {
  bundlerUrl: string
  paymasterUrl: string
  chainId: ChainId
  entryPointAddress: string
}

export class BiconomyWalletHelper {
  private config: BiconomyConfig
  private smartAccount: BiconomySmartAccountV2 | null = null

  constructor(config: BiconomyConfig) {
    this.config = config
  }

  /**
   * Create a new Biconomy Smart Account
   */
  async createSmartWallet(signer: ethers.Signer): Promise<BiconomySmartAccountV2> {
    const biconomyAccountConfig: BiconomySmartAccountV2Config = {
      signer,
      chainId: this.config.chainId,
      bundlerUrl: this.config.bundlerUrl,
      paymasterUrl: this.config.paymasterUrl,
      entryPointAddress: this.config.entryPointAddress,
    }

    this.smartAccount = await BiconomySmartAccountV2.create(biconomyAccountConfig)

    return this.smartAccount
  }

  /**
   * Get the smart wallet address
   */
  async getSmartWalletAddress(): Promise<string> {
    if (!this.smartAccount) {
      throw new Error('Smart account not initialized')
    }
    return await this.smartAccount.getAccountAddress()
  }

  /**
   * Send a transaction using the smart wallet
   */
  async sendTransaction(transaction: {
    to: string
    data: string
    value?: string
  }): Promise<{ userOpHash: string; txHash?: string }> {
    if (!this.smartAccount) {
      throw new Error('Smart account not initialized')
    }

    const userOpResponse = await this.smartAccount.sendTransaction({
      to: transaction.to,
      data: transaction.data,
      value: transaction.value || '0',
    })

    const txHash = await userOpResponse.waitForTxHash()

    return {
      userOpHash: userOpResponse.userOpHash,
      txHash: txHash.transactionHash
    }
  }

  /**
   * Transfer ERC20 tokens
   */
  async transferERC20(
    tokenAddress: string,
    to: string,
    amount: string
  ): Promise<{ userOpHash: string; txHash?: string }> {
    const erc20Interface = new ethers.utils.Interface([
      'function transfer(address to, uint256 amount) returns (bool)',
    ])

    const data = erc20Interface.encodeFunctionData('transfer', [to, amount])

    return this.sendTransaction({
      to: tokenAddress,
      data,
    })
  }

  /**
   * Transfer ETH
   */
  async transferETH(
    to: string,
    amount: string
  ): Promise<{ userOpHash: string; txHash?: string }> {
    return this.sendTransaction({
      to,
      data: '0x',
      value: amount,
    })
  }

  /**
   * Get transaction status
   */
  // async getTransactionStatus(userOpHash: string): Promise<any> {
  //   if (!this.smartAccount) {
  //     throw new Error('Smart account not initialized')
  //   }

  //   return await this.smartAccount.getUserOpHash(userOpHash)
  // }

  /**
   * Get smart account balance
   */
  async getBalance(): Promise<string> {
    if (!this.smartAccount) {
      throw new Error('Smart account not initialized')
    }

    const address = await this.smartAccount.getAccountAddress()
    const provider = this.smartAccount.rpcProvider
    const balance = await provider.getBalance({address: address as Address})
    return ethers.utils.formatEther(balance)
  }

  /**
   * Get ERC20 token balance
   */
  async getERC20Balance(tokenAddress: string): Promise<string> {
    if (!this.smartAccount) {
      throw new Error('Smart account not initialized')
    }

    const address = await this.smartAccount.getAccountAddress()
    const erc20Interface = new ethers.utils.Interface([
      'function balanceOf(address owner) view returns (uint256)',
    ])

    const provider = new ethers.providers.JsonRpcProvider(process.env.WEB3_RPC_URL)
    const contract = new ethers.Contract(tokenAddress, erc20Interface, provider)
    const balance = await contract.balanceOf(address)
    return ethers.utils.formatEther(balance)
  }

  /**
   * Recover smart account using social login or private key
   */
  async recoverSmartAccount(
    signer: ethers.Signer,
    accountAddress?: string
  ): Promise<BiconomySmartAccountV2> {
    const biconomyAccountConfig: BiconomySmartAccountV2Config = {
      signer,
      chainId: this.config.chainId,
      bundlerUrl: this.config.bundlerUrl,
      paymasterUrl: this.config.paymasterUrl,
      entryPointAddress: this.config.entryPointAddress,
    }

    if (accountAddress) {
      biconomyAccountConfig.accountAddress = accountAddress
    }

    this.smartAccount = await BiconomySmartAccountV2.create(biconomyAccountConfig)
    await this.smartAccount.getInitCode()

    return this.smartAccount
  }

  /**
   * Get the current smart account instance
   */
  getSmartAccount(): BiconomySmartAccountV2 | null {
    return this.smartAccount
  }
}

// Default configuration for Mumbai testnet
export const defaultBiconomyConfig: BiconomyConfig = {
  bundlerUrl: `https://bundler.biconomy.io/api/v2/${process.env.NEXT_PUBLIC_BICONOMY_API_KEY}/`,
  paymasterUrl: `https://paymaster.biconomy.io/api/v1/${process.env.NEXT_PUBLIC_BICONOMY_API_KEY}/`,
  chainId: ChainId.POLYGON_MUMBAI,
  entryPointAddress: '0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789',
}

// Factory function to create Biconomy wallet helper
export function createBiconomyWallet(config?: Partial<BiconomyConfig>): BiconomyWalletHelper {
  const finalConfig = { ...defaultBiconomyConfig, ...config }
  return new BiconomyWalletHelper(finalConfig)
} 