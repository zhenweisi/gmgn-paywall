import { useAccount, useConnect, useDisconnect } from 'wagmi'
import { injected } from 'wagmi/connectors'

export default function ConnectWallet() {
  const { address, isConnected } = useAccount()

  const { connect } = useConnect()

  const { disconnect } = useDisconnect()

  if (isConnected) {
    return (
      <button
        onClick={() => disconnect()}
        className="px-5 py-3 rounded-xl bg-red-500 hover:bg-red-600 transition"
      >
        {address?.slice(0, 6)}...{address?.slice(-4)}
      </button>
    )
  }

  return (
    <button
      onClick={() => connect({ connector: injected() })}
      className="px-5 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-500 hover:opacity-90 transition"
    >
      Connect Wallet
    </button>
  )
}