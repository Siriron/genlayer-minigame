# Deployment Guide — Country Clash

## Deployed Contracts

| Contract | Address | Explorer |
|----------|---------|---------|
| stat.py | 0x9706EF854673dDeA6c0F07F3288fFE461a738050 | [View](https://explorer-studio.genlayer.com/tx/0x369dabde85ccb572961c73dbfdac4a1d71f33cc4af66c792a4a5bf40e1df83e8) |
| countryclash_storage.py | 0x3E3C350E026f0C3918FF7c157C2981338165AAd4 | [View](https://explorer-studio.genlayer.com/tx/0x36e0cfc3fa0acba80f893b53a6dc3fca58f175262e99a0e7a5bd5ebfea6d9515) |
| countryclash.py | 0x5fFd3104A2CC3d2c35dB58ebA105eC0b8f25dF10 | [View](https://explorer-studio.genlayer.com/tx/0xc327722f966b29ee54e7edb44c888cfbee4235da782dcca34cd1cf9acd7383b4) |

## Deploy Steps

### 1. Deploy stat.py
1. Go to [studio.genlayer.com](https://studio.genlayer.com)
2. Upload `contracts/stat.py`
3. Deploy — no constructor args
4. Save address

### 2. Deploy countryclash_storage.py
1. Upload `contracts/countryclash_storage.py`
2. Deploy — no constructor args
3. Save address

### 3. Deploy countryclash.py
1. Upload `contracts/countryclash.py`
2. Constructor args:
   - `stat_contract`: stat address
   - `storage_contract`: storage address
3. Deploy — save address

### 4. Add Admin Permissions
- On `stat.py` → call `add_admin` → paste countryclash address
- On `countryclash_storage.py` → call `add_admin` → paste countryclash address

### 5. Update Frontend Config
Open `public/index.html` and update CONFIG:
```javascript
const CONFIG = {
  GAME_CONTRACT: "countryclash address",
  STORAGE_CONTRACT: "storage address",
  STAT_CONTRACT: "stat address",
  RPC_URL: "https://studio.genlayer.com/api",
};
```

### 6. Deploy to Vercel
1. Push repo to GitHub
2. Import to Vercel — Framework: Other
3. Deploy — game live at your Vercel URL
