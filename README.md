# GMGN Paywall Gateway

**Arc Paywall + GMGN / DeepSeek 按次付费网关**  
一个基于 Web3 的付费访问系统，支持 Circle 云托管钱包签名支付，专为 GMGN.ai 工具和 DeepSeek AI 智能分析报告设计。

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![React](https://img.shields.io/badge/React-19+-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6)
![Vite](https://img.shields.io/badge/Vite-5+-646CFF)

## ✨ 核心功能

- **Web3 按次付费**：用户通过 Circle 托管钱包一键支付，获得 GMGN 工具或 DeepSeek 报告访问权限
- **EIP-712 签名支付**：后端使用 Circle Developer Controlled Wallets 安全签名，避免私钥暴露
- **GMGN.ai 工具集成**：`/token`、`/security`、`/wallet`、`/market`、`/track` 等丰富指令
- **DeepSeek AI 智能报告**：调用 DeepSeek 大模型生成机构级量化风控报告（中英双语输出）
- **前后端分离架构**：
  - **Backend**：FastAPI + Web3 + Circle SDK
  - **Frontend**：React 19 + TypeScript + Vite + Wagmi + TanStack Query
- **支持链**：ARC Testnet（主网可轻松切换）、Solana、Base、ETH 等
