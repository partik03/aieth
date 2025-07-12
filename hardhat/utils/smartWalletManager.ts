import { ethers } from 'ethers'
import { BiconomyWalletHelper, createBiconomyWallet } from './biconomyWallet'

export interface SmartWalletState {
  smartAccount: BiconomyWalletHelper | null
  address: string | null
  balance: string | null
  isInitialized: boolean
  isLoading: boolean
  error: string | null
}

export class SmartWalletManager {
  private state: SmartWalletState = {
    smartAccount: null,
    address: null,
    balance: null,
    isInitialized: false,
    isLoading: false,
    error: null,
  }

  private listeners: ((state: SmartWalletState) => void)[] = []

  // Subscribe to state changes
  subscribe(listener: (state: SmartWalletState) => void) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }

  // Notify all listeners of state changes
  private notifyListeners() {
    this.listeners.forEach(listener => listener(this.state))
  }

  // Update state and notify listeners
  private setState(updates: Partial<SmartWalletState>) {
    this.state = { ...this.state, ...updates }
    this.notifyListeners()
  }

  // Get current state
  getState(): SmartWalletState {
    return { ...this.state }
  }

  async initializeWallet(signer: ethers.Signer): Promise<void> {
    try {
      this.setState({ isLoading: true, error: null })

      const biconomyWallet = createBiconomyWallet()
      const smartAccount = await biconomyWallet.createSmartWallet(signer)
      const address = await biconomyWallet.getSmartWalletAddress()
      const balance = await biconomyWallet.getBalance()

      this.setState({
        smartAccount: biconomyWallet,
        address,
        balance,
        isInitialized: true,
        isLoading: false,
        error: null,
      })
    } catch (error) {
      this.setState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to initialize wallet',
      })
      throw error
    }
  }

  async transferETH(to: string, amount: string): Promise<{ userOpHash: string; txHash?: string }> {
    if (!this.state.smartAccount) {
      throw new Error('Smart wallet not initialized')
    }

    try {
      this.setState({ isLoading: true, error: null })
      const result = await this.state.smartAccount.transferETH(to, amount)
      
      // Update balance after transfer
      const newBalance = await this.state.smartAccount.getBalance()
      this.setState({ balance: newBalance, isLoading: false })
      
      return result
    } catch (error) {
      this.setState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Transfer failed',
      })
      throw error
    }
  }

  async transferERC20(tokenAddress: string, to: string, amount: string): Promise<{ userOpHash: string; txHash?: string }> {
    if (!this.state.smartAccount) {
      throw new Error('Smart wallet not initialized')
    }

    try {
      this.setState({ isLoading: true, error: null })
      const result = await this.state.smartAccount.transferERC20(tokenAddress, to, amount)
      this.setState({ isLoading: false })
      
      return result
    } catch (error) {
      this.setState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'ERC20 transfer failed',
      })
      throw error
    }
  }

  async getBalance(): Promise<void> {
    if (!this.state.smartAccount) {
      return
    }

    try {
      const balance = await this.state.smartAccount.getBalance()
      this.setState({ balance })
    } catch (error) {
      this.setState({
        error: error instanceof Error ? error.message : 'Failed to get balance',
      })
    }
  }

  async getTransactionStatus(userOpHash: string): Promise<any> {
    if (!this.state.smartAccount) {
      throw new Error('Smart wallet not initialized')
    }

    return await this.state.smartAccount.getTransactionStatus(userOpHash)
  }

  resetWallet(): void {
    this.setState({
      smartAccount: null,
      address: null,
      balance: null,
      isInitialized: false,
      isLoading: false,
      error: null,
    })
  }

  async recoverWallet(signer: ethers.Signer, accountAddress?: string): Promise<BiconomyWalletHelper> {
    try {
      this.setState({ isLoading: true, error: null })

      const biconomyWallet = createBiconomyWallet()
      const smartAccount = await biconomyWallet.recoverSmartAccount(signer, accountAddress)

      this.setState({ isLoading: false })
      return biconomyWallet
    } catch (error) {
      this.setState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Recovery failed',
      })
      throw error
    }
  }
}

// Global instance
export const smartWalletManager = new SmartWalletManager() 