# GenLayer Mini-Games

A collection of onchain mini-games powered by GenLayer Intelligent Contracts. Each game uses live web data, LLM evaluation, and the GenLayer equivalence principle to create a genuinely decentralized gaming experience.

## 🎮 Games

### 🌍 Country Clash

Two countries. One metric fetched live from the web. Pick the country that ranks higher — fast. Speed bonus rewards quick thinkers.

**Live at:** [genlayer-minigame.vercel.app/countryclash](https://genlayer-minigame.vercel.app/countryclash)

**Metrics:** GDP, Population, Area, Life Expectancy, Inflation Rate

**How it works:**

1. Player picks two countries and a metric
1. The Intelligent Contract fetches live data from the web
1. An LLM determines the correct answer using the equivalence principle
1. Player picks the higher-ranked country within 30 seconds
1. Speed bonus: faster answers earn more points
1. Scores are stored onchain in a shared leaderboard

## 🏗️ Architecture

Each game uses a 3-contract architecture:

|Contract                 |Purpose                                                      |
|-------------------------|-------------------------------------------------------------|
|`countryclash.py`        |Game logic, web fetch, LLM evaluation                        |
|`countryclash_storage.py`|Persistent round archive                                     |
|`stat.py`                |Shared points, nicknames, leaderboard (used across all games)|

## 🚀 Tech Stack

- **Smart Contracts:** Python Intelligent Contracts on GenLayer
- **Frontend:** Pure static HTML/JS — no backend required
- **Deployment:** Vercel (static hosting)
- **Wallet:** MetaMask via window.ethereum

## 📁 Repo Structure

```
/public
  index.html              ← Game hub
  /countryclash
    index.html            ← Country Clash game
/contracts
  countryclash.py         ← Main game contract
  countryclash_storage.py ← Storage contract
  stat.py                 ← Shared stat contract
/vercel.json              ← Routing config
/deployment.md            ← Deployment guide
```

## 🌐 GenLayer Features Used

- `gl.nondet.web.get()` — Live country data fetched from restcountries.com API
- `gl.nondet.exec_prompt()` — LLM determines which country ranks higher
- `gl.eq_principle.strict_eq()` — Ensures consensus across validators
- `TreeMap`, `DynArray` — Onchain data structures
- Admin system — Game contract authorized to write to storage and stat

## 🔗 Links

- Portal: [portal.genlayer.foundation](https://portal.genlayer.foundation)
- Studio: [studio.genlayer.com](https://studio.genlayer.com)
- Docs: [docs.genlayer.com](https://docs.genlayer.com)
