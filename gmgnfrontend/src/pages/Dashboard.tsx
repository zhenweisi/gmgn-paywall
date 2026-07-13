

import { useState, useRef, useEffect } from 'react'
import { useAccount, useConnect, useDisconnect } from 'wagmi'
import { injected } from 'wagmi/connectors'
import { ethers } from 'ethers'
import { CONTRACT_ADDRESS, USDC_ADDRESS, ERC20_ABI, ROUTER_ABI } from '../config/contract'

const FASTAPI_URL = "http://gmgnpaywall.duckdns.org";

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface CommandItem {
  cmd: string;
  desc: string;
  example: string;
}

const COMMAND_LIST: CommandItem[] = [
  { cmd: '/token', desc: 'Audit token metrics, pool liquidity, and short-term K-line status.', example: '/token sol [CA]' },
  { cmd: '/security', desc: 'Deep-dive scan for honey-pots, top holders, and wash-trading risks.', example: '/security base [CA]' },
  { cmd: '/wallet', desc: 'Track whale holdings, real-time tx streams, net PnL, and win-rates.', example: '/wallet sol [Wallet]' },
  { cmd: '/market', desc: 'Live tracking of trending tokens (5m interval) and inner-pool pump creations.', example: '/market' },
  { cmd: '/track', desc: 'Aggregate Smart Money flows and top KOL real-time trading actions.', example: '/track' },
];

export default function Dashboard() {
  const { address: userWallet, isConnected } = useAccount()
  const { connect } = useConnect()
  const { disconnect } = useDisconnect()

  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '🟢 SYSTEM READY // AI Matrix Agent online. Inject target Contract Address or type / to wake up weapon database.' }
  ])
  const [userInput, setUserInput] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [logs, setLogs] = useState<string[]>([])
  
  const [showMenu, setShowMenu] = useState<boolean>(false)
  const [menuIndex, setMenuIndex] = useState<number>(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const logContainerRef = useRef<HTMLDivElement>(null)
  const messageEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`])
  }

  const handleInputChange = (val: string) => {
    setUserInput(val)
    if (val === '/' || val.startsWith('/')) {
      const hasSpace = val.includes(' ')
      setShowMenu(!hasSpace)
    } else {
      setShowMenu(false)
    }
  }

  const selectCommand = (cmd: string) => {
    setUserInput(cmd + " ")
    setShowMenu(false)
    inputRef.current?.focus()
  }

  const handleSendMessage = async () => {
    if (!isConnected || !userWallet) {
      alert("Please connect your MetaMask wallet terminal first!")
      return
    }
    if (!userInput.trim()) return

    const currentPrompt = userInput.trim()
    setMessages(prev => [...prev, { role: 'user', content: currentPrompt }])
    setUserInput("")
    setShowMenu(false)
    setLoading(true)
    setLogs([])
    
    addLog(`SIGNAL // Activating Arc Testnet intent solver & payment router...`)

    try {
      if (!(window as any).ethereum) throw new Error("MetaMask extension not detected")
      const provider = new ethers.BrowserProvider((window as any).ethereum)
      const signer = await provider.getSigner()

      const network = await provider.getNetwork()
      if (Number(network.chainId) !== 5042002) {
        addLog(`WARN // Network mismatch. Requesting switch to Arc Testnet...`)
        try {
          await (window as any).ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0x4cedf6' }], 
          })
        } catch (err) {
          throw new Error("User rejected network switch or target network not configured")
        }
      }

      let calculatedProductType = "scan_report"
      if (currentPrompt.startsWith("/token") || currentPrompt.startsWith("/security")) {
        calculatedProductType = "deep_report"
      }

      addLog(`TRACE // Intent parsed. Triggering [${calculatedProductType}] pricing pipeline. Fetching secure payment payload...`)
      const signRes = await fetch(`${FASTAPI_URL}/v1/payment/signature`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          userWallet, 
          productType: calculatedProductType 
        })
      })
      const backendData = await signRes.json()
      if (!backendData.success) throw new Error(`Backend signature rejected: ${JSON.stringify(backendData)}`)
      
      const { productId, orderId, amount, expiry, signature } = backendData.data
      addLog(`SUCCESS // Circle secure custody signature verified. Order: ${orderId.slice(0, 12)}...`);

      addLog(`PROMPT // Requesting contract token allowance for ${(amount/1000000).toFixed(2)} USDC...`)
      const usdcContract = new ethers.Contract(USDC_ADDRESS, ERC20_ABI, signer)
      const approveTx = await usdcContract.approve(CONTRACT_ADDRESS, amount)
      addLog(`WAIT // Allowance pending... Tx Hash: ${approveTx.hash}`)
      await approveTx.wait()
      addLog("SUCCESS // USDC on-chain allowance clearance settled.")

      addLog("PROMPT // Triggering pay() core contract entrypoint. Awaiting non-custodial execution...")
      const routerContract = new ethers.Contract(CONTRACT_ADDRESS, ROUTER_ABI, signer)
      const payTx = await routerContract.pay(productId, orderId, amount, expiry, signature)
      addLog(`WAIT // Block verification in progress... Tx Hash: ${payTx.hash}`)
      await payTx.wait()
      addLog("SUCCESS // Payment cleared! Paid event emitted on Arc Layer.")

      addLog("PENDING // Synchronizing off-chain database and ledger records...")
      await new Promise(resolve => setTimeout(resolve, 3000))

      addLog("PIPELINE // Alpha Risk Engine (ARE) activated. Compiling cross-chain toolchain metrics via gmgn-cli...")
      const chatRes = await fetch(`${FASTAPI_URL}/v1/report/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          productType: calculatedProductType,
          userWallet, 
          targetToken: currentPrompt, 
          orderId: orderId 
        }) 
      })
      const chatData = await chatRes.json()
      if (chatRes.status !== 200) throw new Error(chatData.detail || "Data release rejected by risk core")
      
      const aiReply = chatData.data?.report || "Empty response from analysis engine"
      
      setMessages(prev => [...prev, { role: 'assistant', content: aiReply }])
      addLog("LOCKED // Mission Cleared. Institutional analysis decrypted and fully rendered.")

    } catch (err: any) {
      const errMsg = err.message || err
      addLog(`CRITICAL // Exception trapped: ${errMsg}`)
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ CRITICAL_ERROR // Execution broken: ${errMsg}` }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (showMenu) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setMenuIndex(prev => (prev + 1) % COMMAND_LIST.length)
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setMenuIndex(prev => (prev - 1 + COMMAND_LIST.length) % COMMAND_LIST.length)
      } else if (e.key === 'Enter') {
        e.preventDefault()
        selectCommand(COMMAND_LIST[menuIndex].cmd)
      } else if (e.key === 'Escape') {
        setShowMenu(false)
      }
    } else {
      if (e.key === 'Enter' && !loading) {
        handleSendMessage()
      }
    }
  }

  return (
    <div className="min-h-screen bg-[#070a0e] text-slate-200 font-mono flex flex-col antialiased selection:bg-emerald-500/30">
      
      <header className="border-b border-emerald-500/10 bg-[#0c121a]/80 backdrop-blur-md sticky top-0 z-50 px-8 py-4 flex items-center justify-between shadow-[0_1px_20px_rgba(16,185,129,0.02)] flex-shrink-0">
        <div className="flex items-center space-x-3">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_#10b981]" />
          <h1 className="text-sm font-black tracking-[0.2em] uppercase text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
            ARC INTENT MEME-MATRIX ENGINE // v2.4
          </h1>
        </div>
        
        {isConnected ? (
          <button 
            onClick={() => disconnect()}
            className="group flex items-center space-x-2 bg-[#0d151f] border border-emerald-500/20 hover:border-red-500/40 px-4 py-1.5 rounded transition-all duration-300 text-xs font-bold"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 group-hover:bg-red-400 transition-colors" />
            <span className="text-emerald-400/80 group-hover:text-red-400 transition-colors tracking-wider">
              {userWallet?.slice(0, 6)}...{userWallet?.slice(-4)}
            </span>
            <span className="text-[9px] text-slate-500 group-hover:text-red-400 uppercase tracking-widest pl-2 border-l border-slate-800 ml-1">Disconnect</span>
          </button>
        ) : (
          <button 
            onClick={() => connect({ connector: injected() })}
            className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 px-5 py-1.5 rounded text-xs font-black tracking-widest uppercase shadow-lg shadow-emerald-500/10 transition-all active:scale-95"
          >
            🔌 Connect Terminal
          </button>
        )}
      </header>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 min-h-0 overflow-hidden">
        
        <section className="lg:col-span-7 flex flex-col bg-[#0b1118]/90 border border-emerald-500/10 rounded shadow-[0_0_30px_rgba(16,185,129,0.02)] relative overflow-hidden group hover:border-emerald-500/20 transition-all duration-300">
          <div className="px-5 py-3 border-b border-emerald-500/10 bg-[#0e1722]/60 flex items-center justify-between flex-shrink-0">
            <span className="text-xs uppercase font-black tracking-widest text-emerald-400 flex items-center space-x-2">
              <span className="inline-block w-1.5 h-1.5 bg-emerald-400 rounded-sm animate-ping" />
              <span>Smart Analytics</span>
            </span>
            <span className="text-[10px] text-slate-600 font-bold tracking-wider">PANEL_ID // 03</span>
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto custom-scrollbar space-y-4 min-h-0">
            {messages.map((msg, idx) => {
              const isAssistant = msg.role === 'assistant';
              return (
                <div key={idx} className={`flex ${isAssistant ? 'justify-start' : 'justify-end'}`}>
                  <div className={`w-full font-mono rounded p-4 border leading-7 text-xs ${
                    isAssistant 
                      ? 'bg-transparent border-slate-900 text-slate-300' 
                      : 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.03)]'
                  }`}>
                    {isAssistant ? (
                      <div className="whitespace-pre-wrap">
                        {msg.content.split('\n').map((line, lineIdx) => {
                          const cleanLine = line.trim();
                          if (!cleanLine) return <div key={lineIdx} className="h-2" />;
                          
                          if (cleanLine.startsWith('### 🟢') || cleanLine.includes('SYSTEM HEALTH')) {
                            return <div key={lineIdx} className="text-sm font-black text-emerald-400 bg-emerald-950/20 p-3 rounded border border-emerald-500/20 my-2 shadow-[0_0_15px_rgba(16,185,129,0.05)] uppercase tracking-wider">{cleanLine.replace('### ', '')}</div>;
                          }
                          if (cleanLine.startsWith('### 🛡️') || cleanLine.includes('RISK EXPOSURE')) {
                            const sideParts = cleanLine.split('(');
                            return <div key={lineIdx} className="text-xs font-bold text-teal-400 bg-[#0f1822] p-3 rounded border border-emerald-500/10 my-2 flex justify-between uppercase"><span>{sideParts[0].replace('### ', '')}</span><span className="text-emerald-400 font-black">{sideParts[1]?.replace(')', '') || '18.7%'}</span></div>;
                          }
                          if (cleanLine.startsWith('### 💵') || cleanLine.includes('CAPITAL DEPLOYED')) {
                            return <div key={lineIdx} className="text-[11px] tracking-wider text-slate-500 border-b border-slate-800/60 pb-2 mb-3 font-bold uppercase">{cleanLine.replace('### ', '')}</div>;
                          }
                          if (cleanLine.startsWith('### ')) {
                            return <h4 key={lineIdx} className="text-emerald-500 font-black tracking-widest text-[11px] uppercase mt-5 mb-1.5 flex items-center">➔ {cleanLine.replace('### ', '')}</h4>;
                          }
                          if (cleanLine.startsWith('* ')) {
                            return <div key={lineIdx} className="pl-4 py-0.5 text-slate-400 hover:text-slate-200 transition-colors text-[11px] flex items-start"><span className="text-emerald-500/60 mr-1.5">▪</span><span>{cleanLine.replace('* ', '')}</span></div>;
                          }
                          return <div key={lineIdx} className="text-slate-300 leading-relaxed py-0.5">{line}</div>;
                        })}
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap font-bold tracking-wider text-emerald-400">&gt;_ {msg.content}</div>
                    )}
                  </div>
                </div>
              );
            })}
            <div ref={messageEndRef} />
          </div>

          {showMenu && (
            <div className="absolute bottom-[75px] left-4 right-4 bg-[#090f15] border border-emerald-500/20 rounded shadow-[0_0_40px_rgba(0,0,0,0.9)] z-50 max-h-[220px] overflow-y-auto p-1 font-mono text-[11px]">
              <div className="p-2 text-slate-500 border-b border-slate-900 font-black uppercase tracking-widest text-[9px] flex justify-between">
                <span>⌨️ QUANT TERMINAL WEAPONS BAY</span>
                <span className="text-emerald-500/60 font-medium">PRESS ENTER TO INJECT</span>
              </div>
              {COMMAND_LIST.map((item, index) => (
                <div 
                  key={item.cmd}
                  onClick={() => selectCommand(item.cmd)}
                  onMouseEnter={() => setMenuIndex(index)}
                  className={`p-2.5 rounded transition flex flex-col gap-0.5 cursor-pointer ${
                    index === menuIndex ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' : 'text-slate-400 hover:bg-slate-900/40'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-black text-xs text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">{item.cmd}</span>
                    <span className="text-[9px] text-slate-600">EG: {item.example}</span>
                  </div>
                  <div className="text-slate-400 text-[10px] tracking-wide">{item.desc}</div>
                </div>
              ))}
            </div>
          )}

          <div className="p-4 border-t border-emerald-500/10 bg-[#090e14]/90 backdrop-blur-sm flex-shrink-0">
            <div className="relative flex items-center bg-[#0d151f] border border-slate-800/80 focus-within:border-emerald-500/40 rounded p-1 transition-all shadow-[inner_0_0_15px_rgba(0,0,0,0.6)]">
              <span className="pl-3 text-emerald-500 font-black text-xs select-none">&gt;_</span>
              <input
                ref={inputRef}
                type="text" 
                value={userInput} 
                onChange={(e) => handleInputChange(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Inject command or paste target CA / Wallet address here..."
                disabled={loading || !isConnected}
                className="w-full bg-transparent border-0 outline-none focus:ring-0 px-3 py-2 text-xs text-emerald-400 font-mono placeholder-slate-700 tracking-wider disabled:cursor-not-allowed"
              />
              <button 
                onClick={handleSendMessage}
                disabled={loading || !isConnected || !userInput.trim()}
                className={`text-slate-950 font-black text-xs px-6 py-2.5 rounded-sm tracking-[0.2em] uppercase transition-all flex items-center flex-shrink-0 ${
                  !isConnected 
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed shadow-none' 
                    : loading 
                      ? 'bg-teal-600 text-slate-950 cursor-wait animate-pulse' 
                      : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 shadow-[0_0_15px_rgba(16,185,129,0.2)] active:scale-95'
                }`}
              >
                {loading ? "LOCKING..." : "LAUNCH"}
              </button>
            </div>
          </div>
        </section>

        {/* 右舱：控制台实时追踪日志 */}
        <section className="lg:col-span-5 flex flex-col bg-[#080d13] border border-slate-900 rounded shadow-2xl relative overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-900 bg-[#0b121a]/90 flex items-center justify-between flex-shrink-0">
            <span className="text-xs uppercase font-black tracking-widest text-slate-400 flex items-center space-x-2">
              <span className="w-1.5 h-1.5 rounded-sm bg-slate-500 animate-pulse" />
              <span>Execution Console</span>
            </span>
            <span className="text-[9px] text-slate-600 font-mono tracking-widest">STREAM // ACTIVE</span>
          </div>
          
          <div 
            ref={logContainerRef}
            className="flex-1 p-4 bg-[#05080c]/60 overflow-y-auto space-y-2 text-[10px] font-mono custom-scrollbar min-h-0"
          >
            {logs.length === 0 ? (
              <div className="text-slate-700 h-full flex items-center justify-center tracking-widest text-[9px] uppercase animate-pulse">
                💬 SYSTEM IDLE // Awaiting command injector activation...
              </div>
            ) : (
              logs.map((log, index) => {
                const isSuccess = log.includes("SUCCESS") || log.includes("LOCKED");
                const isWait = log.includes("WAIT") || log.includes("PENDING") || log.includes("SIGNAL") || log.includes("TRACE") || log.includes("PROMPT") || log.includes("PIPELINE");
                const isCritical = log.includes("CRITICAL") || log.includes("WARN");
                
                let rowStyle = "bg-slate-900/20 border-slate-900/60 text-slate-500";
                if (isSuccess) rowStyle = "bg-emerald-950/10 border-emerald-500/10 text-emerald-400 font-bold shadow-[0_0_10px_rgba(16,185,129,0.01)]";
                if (isWait) rowStyle = "bg-teal-950/5 border-teal-500/10 text-teal-400/90";
                if (isCritical) rowStyle = "bg-red-950/20 border-red-500/20 text-red-400 font-black";

                return (
                  <div 
                    key={index} 
                    className={`p-2 border rounded-sm transition-all duration-200 tracking-wide leading-5 break-all ${rowStyle}`}
                  >
                    {log}
                  </div>
                );
              })
            )}
          </div>
        </section>
      </main>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #111c26; border-radius: 2px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #059669; }
      `}</style>
    </div>
  )
}
