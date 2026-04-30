# GenLayer Mini-Games

A collection of onchain mini-games powered by GenLayer Intelligent Contracts. Each game uses live web data, LLM evaluation, and the GenLayer equivalence principle to create a genuinely decentralized gaming experience.

## 🎮 Games

### 🌍 Country Clash
Two countries. One metric fetched live from the web. Pick the country that ranks higher — fast. Speed bonus rewards quick thinkers.

**Live at:** [genlayer-minigame.vercel.app/countryclash](https://genlayer-minigame.vercel.app/countryclash)

**Metrics:** GDP, Population, Area, Life Expectancy, Inflation Rate

**How it works:**
1. Player picks two countries and a metric
2. The Intelligent Contract fetches live data from the web
3. An LLM determines the correct answer using the equivalence principle
4. Player picks the higher-ranked country within 30 seconds
5. Speed bonus: faster answers earn more points
6. Scores are stored onchain in a shared leaderboard

---

### 📰 Headline Hoax
One headline is real. One is AI-generated. Can you spot the fake? Pick the real headline before time runs out.

**Live at:** [genlayer-minigame.vercel.app/headlinehoax](https://genlayer-minigame.vercel.app/headlinehoax)

**Topics:** World News, Tech, Crypto, Science, Sports

**How it works:**
1. Player picks a topic
2. The Intelligent Contract fetches a real headline from the web
3. An LLM generates a convincing fake headline on the same topic
4. Player picks which headline is real within 30 seconds
5. Speed bonus: faster answers earn more points
6. Scores stored onchain in the shared leaderboard

---

## 🏗️ Architecture

Each game uses a 3-contract architecture:

| Contract | Purpose |
|----------|---------|
| `game.py` | Game logic, web fetch, LLM evaluation |
| `game_storage.py` | Persistent round archive |
| `stat.py` | Shared points, nicknames, leaderboard (used across all games) |

## 🚀 Tech Stack

- **Smart Contracts:** Python Intelligent Contracts on GenLayer
- **Frontend:** Pure static HTML/JS — no backend required
- **Deployment:** Vercel (static hosting)
- **Wallet:** MetaMask via window.ethereum

## 📁 Repo Structure

```
/public
  index.html                    ← Game hub
  /countryclash
    index.html                  ← Country Clash game
  /headlinehoax
    index.html                  ← Headline Hoax game
/contracts
  countryclash.py
  countryclash_storage.py
  headlinehoax.py
  headlinehoax_storage.py
  stat.py                       ← Shared across all games
/vercel.json
/README.md
/deployment.md
```

## 🌐 GenLayer Features Used

- `gl.nondet.web.get()` — Live data fetched from the web mid-game
- `gl.nondet.exec_prompt()` — LLM generates fake headlines and evaluates answers
- `gl.eq_principle.strict_eq()` — Ensures consensus across validators
- `TreeMap`, `DynArray` — Onchain data structures
- Admin system — Game contracts authorized to write to storage and stat

## 📋 Deployed Contracts

| Contract | Address |
|----------|---------|
| stat.py | 0x9706EF854673dDeA6c0F07F3288fFE461a738050 |
| countryclash_storage.py | 0x3E3C350E026f0C3918FF7c157C2981338165AAd4 |
| countryclash.py | 0x5fFd3104A2CC3d2c35dB58ebA105eC0b8f25dF10 |
| headlinehoax_storage.py | 0xC0378B36041bCAa14feA5F8De1430bB0d0631D8a |
| headlinehoax.py | 0xCd7E16F924bA8fd92f06C02610F2641F874b08C4 |

## 🔗 Links

- Portal: [portal.genlayer.foundation](https://portal.genlayer.foundation)
- Studio: [studio.genlayer.com](https://studio.genlayer.com)
- Docs: [docs.genlayer.com](https://docs.genlayer.com)
- 
