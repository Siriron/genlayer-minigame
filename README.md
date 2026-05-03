
# Country Clash — GenLayer Intelligent Contract Game

A live-data onchain mini-game built on GenLayer. Two countries appear on screen with a real-world metric. The player picks which country ranks higher within 30 seconds. Speed bonus rewards faster correct answers.

**Live at:** [genlayer-minigame.vercel.app](https://genlayer-minigame.vercel.app)

## How it works

1. Player picks two countries and a metric (GDP, Population, Area, Life Expectancy, Inflation Rate)
2. The Intelligent Contract fetches live country data from the web using `gl.nondet.web.get()`
3. An LLM determines the correct answer using `gl.eq_principle.strict_eq()`
4. Player picks the higher-ranked country within 30 seconds
5. Speed bonus: faster answers earn more points
6. Scores stored onchain in a shared leaderboard

## 🌐 GenLayer Features Used

- `gl.nondet.web.get()` — Live country data fetched from restcountries.com
- `gl.nondet.exec_prompt()` — LLM determines which country ranks higher
- `gl.eq_principle.strict_eq()` — Ensures consensus across validators
- `TreeMap`, `DynArray` — Onchain data structures
- Admin system — Game contract authorized to write to storage and stat

## 🏗️ Architecture

| Contract | Purpose |
|----------|---------|
| `countryclash.py` | Game logic, web fetch, LLM evaluation |
| `countryclash_storage.py` | Persistent round archive |
| `stat.py` | Points, nicknames, leaderboard |

## 📋 Deployed Contracts

| Contract | Address |
|----------|---------|
| stat.py | 0x9706EF854673dDeA6c0F07F3288fFE461a738050 |
| countryclash_storage.py | 0x3E3C350E026f0C3918FF7c157C2981338165AAd4 |
| countryclash.py | 0x5fFd3104A2CC3d2c35dB58ebA105eC0b8f25dF10 |

## 🚀 Tech Stack

- **Smart Contracts:** Python Intelligent Contracts on GenLayer
- **Frontend:** Pure static HTML/JS — no backend
- **Deployment:** Vercel

## 📁 Repo Structure

```
/public
  index.html              ← Game frontend
/contracts
  countryclash.py
  countryclash_storage.py
  stat.py
/vercel.json
/README.md
/deployment.md
```

## 🔗 Links

- Portal: [portal.genlayer.foundation](https://portal.genlayer.foundation)
- Studio: [studio.genlayer.com](https://studio.genlayer.com)
- Explorer: [explorer-studio.genlayer.com](https://explorer-studio.genlayer.com)
- 
