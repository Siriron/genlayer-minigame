# Deployment Guide — GenLayer Mini-Games

## Prerequisites

- MetaMask wallet with GenLayer testnet configured
- Account on [studio.genlayer.com](https://studio.genlayer.com)
- Vercel account connected to your GitHub

-----

## Step 1 — Deploy Stat Contract

The stat contract is shared across all games. Deploy it once.

1. Go to [studio.genlayer.com](https://studio.genlayer.com)
1. Click **Upload Contract**
1. Upload `contracts/stat.py`
1. Click **Deploy**
1. Copy the deployed contract address — save it as `STAT_CONTRACT`

-----

## Step 2 — Deploy Storage Contract

1. Upload `contracts/countryclash_storage.py`
1. Click **Deploy** (no constructor args needed)
1. Copy the address — save it as `STORAGE_CONTRACT`

-----

## Step 3 — Deploy Game Contract

1. Upload `contracts/countryclash.py`
1. In the constructor fields enter:
- `stat_contract`: paste `STAT_CONTRACT` address
- `storage_contract`: paste `STORAGE_CONTRACT` address
1. Click **Deploy**
1. Copy the address — save it as `GAME_CONTRACT`

-----

## Step 4 — Add Admin Permissions

The game contract must be authorized to write to both storage and stat contracts.

**On the Storage contract:**

1. Go to your `countryclash_storage` contract in Studio
1. Call `add_admin`
1. Paste your `GAME_CONTRACT` address
1. Submit

**On the Stat contract:**

1. Go to your `stat` contract in Studio
1. Call `add_admin`
1. Paste your `GAME_CONTRACT` address
1. Submit

-----

## Step 5 — Update Frontend Config

Open `public/countryclash/index.html` and find the CONFIG block near the top of the script:

```javascript
const CONFIG = {
  GAME_CONTRACT: "YOUR_COUNTRYCLASH_CONTRACT_ADDRESS",
  STORAGE_CONTRACT: "YOUR_STORAGE_CONTRACT_ADDRESS",
  STAT_CONTRACT: "YOUR_STAT_CONTRACT_ADDRESS",
  RPC_URL: "https://studio.genlayer.com/api",
};
```

Replace the placeholder values with your deployed contract addresses.

-----

## Step 6 — Deploy to Vercel

1. Push the repo to GitHub
1. Go to [vercel.com](https://vercel.com) → **New Project**
1. Import your GitHub repo
1. Framework Preset: **Other**
1. Root Directory: leave as default (repo root)
1. Click **Deploy**

Vercel will detect `vercel.json` and configure routing automatically.

Your game will be live at:

- `https://genlayer-minigame.vercel.app/` — Game hub
- `https://genlayer-minigame.vercel.app/countryclash` — Country Clash
- `https://genlayer-minigame.vercel.app/headlinehoax` — headlinehoax
-----

## Contract Addresses (fill after deploy)

|Contract               |Address                                   |
|-----------------------|------------------------------------------|
|stat.py                |0x9706EF854673dDeA6c0F07F3288fFE461a738050|
|countryclash_storage.py|0x3E3C350E026f0C3918FF7c157C2981338165AAd4|
|countryclash.py        |0x5fFd3104A2CC3d2c35dB58ebA105eC0b8f25dF10|
| headlinehoax_storage.py | 0xC0378B36041bCAa14feA5F8De1430bB0d0631D8a |
| headlinehoax.py | 0xCd7E16F924bA8fd92f06C02610F2641F874b08C4 |
-----

## Adding Future Games

1. Create `contracts/newgame.py` + `contracts/newgame_storage.py`
1. Deploy both, add game contract as admin to storage + stat
1. Create `public/newgame/index.html`
1. Add route to `vercel.json`
1. Push to GitHub — Vercel auto-redeploys
1. Submit new portal contribution with the new game route URL
