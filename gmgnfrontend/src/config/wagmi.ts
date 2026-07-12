import { createConfig, http } from 'wagmi'
import { injected } from 'wagmi/connectors'

// 严格对齐你的 CHAIN_ID = 5042002 和官方 RPC
export const arcTestnet = {
  id: 5042002,
  name: 'Arc Testnet',
  nativeCurrency: {
    name: 'USDC',
    symbol: 'USDC',
    decimals: 6,
  },
  rpcUrls: {
    default: {
      http: ['https://rpc.testnet.arc.network'],
    },
  },
} as const

export const config = createConfig({
  chains: [arcTestnet],
  connectors: [injected()], // 纯粹调起小狐狸插件
  transports: {
    [arcTestnet.id]: http(),
  },
})