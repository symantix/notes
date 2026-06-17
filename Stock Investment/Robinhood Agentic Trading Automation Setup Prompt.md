# Robinhood Agentic Trading Automation Setup Prompt

Created: 2026-06-04

Use this note if the Codex stock automation system ever needs to be rebuilt, audited, or transferred. It is written as a setup prompt for a future agent.

## Prompt For The Agent

You are setting up Joey's Robinhood Agentic Trading automation system in Codex. This is a real-money, high-risk stock automation system. Do not place trades during setup unless Joey explicitly asks for a live trading run. Your job is to restore the automation prompts, shared strategy file, shared strategy/planning ledger, schedules, writable paths, and review loop.

First inspect the current filesystem and Codex automations. Preserve any existing newer files or automation definitions unless Joey explicitly asks you to replace them. If this is a repo-tracked edit, refresh the remote default branch first and do not disturb unrelated local changes.

## Core Files

Use these paths:

- Shared strategy prompt: `/Users/joey/Documents/Codex/robinhood-agentic-trading-strategy.md`
- Shared strategy/planning ledger: `/Users/joey/Documents/Codex/robinhood-agentic-trading-ledgers/strategy-planning-ledger.md`
- Compatibility symlink: `/Users/joey/Documents/Codex/robinhood-agentic-trading-news-sources.md`
- Compatibility symlink: `/Users/joey/Documents/Codex/2026-06-01/let-s-set-this-up/work/.codex/robinhood-agentic-trading-news-sources.md`
- Shared daily trading memory: `/Users/joey/.codex/automations/robinhood-agentic-trading-daily-review/memory.md`
- Evening memory path: `/Users/joey/.codex/automations/robinhood-agentic-trading-evening-posture-review/memory.md`

All active stock automations should use:

```toml
execution_environment = "local"
cwds = ["/Users/joey/Documents/Codex"]
model = "gpt-5.5"
reasoning_effort = "xhigh"
```

The `cwds` value matters. It keeps the shared ledger inside the startup writable root before Joey joins an automation chat.

## Automation Inventory

Create or verify these Codex cron automations.

| Automation id | Name | Schedule | Run type |
| --- | --- | --- | --- |
| `robinhood-agentic-trading-morning-preflight` | Robinhood Agentic Trading Morning Preflight | Weekdays 8:20 AM local | Preparation and triage before regular-hours action |
| `robinhood-agentic-trading-daily-review` | Robinhood Agentic Trading Daily Review | Weekdays 8:35 AM local | Primary morning action window |
| `robinhood-agentic-trading-midday-risk-review` | Robinhood Agentic Trading Midday Risk Review | Weekdays 12:15 PM local | Risk, trend, and deterioration check |
| `robinhood-agentic-trading-evening-posture-review` | Robinhood Agentic Trading Evening Posture Review | Sunday through Thursday 7:30 PM local | Overnight posture and next-session plan |
| `robinhood-agentic-trading-weekly-strategy-review` | Robinhood Agentic Trading Weekly Strategy Review | Sundays 5:30 PM local | No-trade strategy review and learning loop |

Optional one-time probe automations may exist:

- `robinhood-ledger-writability-probe-1420`
- `robinhood-ledger-writability-probe-1520`

These probes only test whether `/Users/joey/Documents/Codex/robinhood-agentic-trading-ledgers/strategy-planning-ledger.md` is writable at automation startup. They must not use Robinhood or edit the ledger.

## Thin Automation Prompt Pattern

Each daily stock automation should be a thin wrapper. It should not duplicate the full strategy. It should say:

1. Use the configured `robinhood-trading` MCP server.
2. This is Joey's real-money, high-risk Robinhood Agentic Trading automation.
3. Read the automation's own memory first when available.
4. Read and follow `/Users/joey/Documents/Codex/robinhood-agentic-trading-strategy.md`.
5. Read `/Users/joey/Documents/Codex/robinhood-agentic-trading-ledgers/strategy-planning-ledger.md`.
6. Read shared daily trading memory when available.
7. Use the run type's session profile from the shared strategy.
8. Always send the required OS-level completion notification before returning.

The weekly strategy review prompt is different: it is explicitly no-trade. It may fetch account/order/position and market data only to evaluate outcomes and update the ledger. It must not run order reviews, place trades, or cancel orders.

## Shared Strategy Requirements

The shared strategy file must include these ideas:

- Use only the configured `robinhood-trading` MCP server.
- Trade only in Joey's Robinhood Agentic account, not the default non-agentic margin account.
- Standing pre-approval applies only to qualifying individual publicly traded stock buys, sells, trims, and safe equity-order cancellations in the Agentic account.
- Use only broker-reported available buying power/cash and sellable long shares.
- No ETFs, options, crypto, futures, event contracts, margin, borrowing, short sales, naked shorts, leverage, or positions that can lose more than the cash committed unless Joey explicitly approves the exception in the current run.
- If the shared strategy file is unavailable, stale, ambiguous, or conflicts with stricter current instructions, do not place orders or cancel orders.
- Always read the shared strategy/planning ledger before research, account work, or trade decisions.
- Always check planning notes, position theses, decision outcomes awaiting review, catalyst calendar items, and risk-budget rules.
- Always fetch current account, buying power, positions, sellable shares, recent orders, today's filled orders, quotes, and tradability as needed.
- Run `review_equity_order` before any real order unless a stricter current instruction explicitly says otherwise.
- Place an order only if broker `order_checks` are empty and the account, security, session, and order parameters are unambiguous.
- Refresh portfolio and positions after each order before considering another trade.
- Include exact order parameters, order id, fill status, and average fill price when applicable.
- Avoid same-day round-trip sells unless risk is severe and the report includes a line beginning exactly `DAY-TRADING RADAR WARNING:`.
- Always send an OS-level notification before returning. Prefer escalated macOS `osascript` GUI notification.

## Strategy/Planning Ledger Schema

The ledger should include these sections.

### Scoring Rules

Define source scores from 0 to 100. Reward sources that helped identify profitable opportunities, timely exits, or avoided losses. Penalize sources that were late, noisy, misleading, contradicted by higher-quality data, or contributed to bad trades.

### Planning Note Rules

Use planning notes for cross-run handoffs, next-session watchlists, candidate actions, timing triggers, risk checks, order-prep ideas, and unresolved decisions.

Statuses:

- `Open`
- `Waiting`
- `Acted`
- `Superseded`
- `Closed`

Every stock automation checks all `Open` and `Waiting` notes and updates status when it acts, rejects, waits, or finds the note stale.

### Decision Outcome Rules

Log every real buy, sell, trim, cancellation, avoided trade, and high-conviction watchlist call.

Track:

- Date
- Run
- Symbol
- Decision type
- Action or non-action
- Thesis snapshot
- Confidence
- Horizon
- Entry or skip price
- Outcome 1D
- Outcome 3D
- Outcome 1W
- Outcome 1M
- Decision quality
- Lesson/follow-up

Decision quality can be `Good`, `Mixed`, `Bad`, or `Pending`.

### Risk Budget Rules

Use risk buckets before sizing:

- Core compounder
- Catalyst growth
- Speculative high-risk
- Rescue/replacement buy after sale
- Watchlist only

Use bucket max new-buy and max-position guidance as caps, then tighten for weak evidence, spread, liquidity, event risk, concentration, correlation, and current account state.

Do not average down automatically. Require a refreshed thesis and explicit exit trigger.

### Rule And Tax Watch

This is not tax or legal advice, but automations should surface practical issues:

- Cash-account settlement, free-riding, and good-faith risk
- Frequent intraday trading and day-trading radar
- Wash-sale risk after loss sales and quick rebuy plans
- Prohibited margin, leverage, short, options, crypto, ETF, futures, or event-contract exposure

### Position Thesis And Exit Triggers

Maintain one row per current holding:

- Symbol
- Status
- Entry/add date
- Current thesis
- Key sources
- Expected catalyst/horizon
- What invalidates the thesis
- Trim/sell trigger
- Do-not-sell-before condition
- Last reviewed

If a holding is missing, the next stock automation should add it before making a hold/sell/trim decision.

### Catalyst Calendar

Track earnings, macro data, FDA/regulatory events, analyst days, product launches, lockups, and other timing-sensitive catalysts. Close or update stale rows.

### Weekly Strategy Review Log

The weekly review appends one row per review after checking matured source notes, decision outcomes, position theses, catalyst calendar, planning notes, and risk-budget performance.

## Session Profiles

### Morning Preflight

Prepare and triage. Review overnight and premarket news, current affairs, open orders, positions, available cash/buying power, and candidate order ideas. Prefer a prepared plan/watchlist over forcing premarket execution. Record useful plans and unresolved checks in the ledger for the morning review.

### Morning Daily Review

Primary action window. Review holdings for sell/trim risk before deploying cash. If regular-hours market data is live and the Agentic account has buying power, look for the best risk/reward individual-stock buys. If fully invested and no sell is justified, provide a watchlist only.

### Mid-Day Risk Review

Risk and trend check, not a churn engine. Act only when risk has deteriorated, a thesis has failed, an intraday trend is clearly breaking, or available buying power can be deployed into a materially better opportunity.

### Evening Posture Review

Posture review for overnight risk and the next trading day. Be cautious with after-hours execution. Prefer next-session action plans and watchlists unless standing pre-approval, broker review, and risk/reward strongly support action. Record actionable planning notes for morning preflight and morning review.

### Weekly Strategy Review

No-trade review loop. Review mature outcomes, update source scores and decision-quality fields, prune stale plans, close stale catalysts, adjust risk-budget guidance, and append a weekly strategy review log row. Do not review, place, or cancel orders.

## Verification Checklist

After setup:

1. Confirm the strategy file exists.
2. Confirm the strategy/planning ledger exists.
3. Confirm old source-ledger compatibility paths are symlinks to the strategy/planning ledger.
4. Confirm all stock automations use `cwds = ["/Users/joey/Documents/Codex"]`.
5. Confirm all stock automation TOML files parse.
6. Confirm the weekly strategy review is active, no-trade, and scheduled Sunday 5:30 PM local time.
7. Confirm the daily automations read the shared strategy rather than duplicating it.
8. Confirm the ledger includes planning notes, decision outcomes, risk budget rules, rule/tax watch, position theses, catalyst calendar, source outcome notes, and weekly review log.
9. Confirm no setup run placed trades or cancelled orders.

## Current Canonical Setup As Of 2026-06-04

- Shared strategy: `/Users/joey/Documents/Codex/robinhood-agentic-trading-strategy.md`
- Shared ledger: `/Users/joey/Documents/Codex/robinhood-agentic-trading-ledgers/strategy-planning-ledger.md`
- Daily stock automations: morning preflight, morning daily review, mid-day risk review, evening posture review
- Weekly no-trade review automation: weekly strategy review
- Model for active stock automations: `gpt-5.5`
- Reasoning effort: `xhigh`
- Startup cwd: `/Users/joey/Documents/Codex`
- Core principle: daily automations make decisions; the ledger makes the system remember and improve.
