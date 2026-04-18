---
title: TradingView
type: entity
domain: finance
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[Claude Can Now TRADE For You On TradingView (Insane)]]"
tags:
  - tradingview
  - trading
  - charting
  - mcp
---

# TradingView

Charting and technical analysis platform used as the market data source in [[algorithmic-trading-with-llms|LLM trading workflows]].

## Role in AI Trading Architecture

TradingView provides:
- Live price charts and candlestick data
- Technical indicators (VWAP, EMA, RSI, etc.)
- Pine Script for custom indicator/strategy definitions
- MCP (Model Context Protocol) connection to [[claude-code]]

In the architecture from [[claude-tradingview-trading]], TradingView is the data source. It does NOT connect directly to the exchange. Claude Code sits between TradingView and the exchange, acting as the decision/safety layer.

## Connection to Claude Code

Via MCP integration (setup covered in Lewis Jackson's prerequisite video). Once connected, Claude can:
- Read live chart data
- Check indicator values
- Draw lines on charts
- Monitor signal conditions
- Apply strategies defined in rules.json

## See also

- [[algorithmic-trading-with-llms]]
- [[claude-tradingview-trading]]
- [[claude-code]]
