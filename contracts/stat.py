# { “Depends”: “py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6” }

from genlayer import *
from dataclasses import dataclass
import typing
import json

@allow_storage
@dataclass
class GameArchive:
is_creator: bool
game_time: str
game_id: str
game_type: u256

```
def to_dict(self):
    return {
        "id": self.game_id,
        "creator": str(self.is_creator),
        "game_time": self.game_time,
        "game_type": str(self.game_type)
    }
```

class UserStat(gl.Contract):
owner: Address
admins: DynArray[Address]
points: TreeMap[Address, u256]
points_by_game: TreeMap[Address, TreeMap[u256, u256]]
nicknames: TreeMap[Address, str]
games_archive: TreeMap[Address, TreeMap[str, GameArchive]]
error: str

```
def __init__(self) -> None:
    self.owner = gl.message.sender_address
    self.admins.append(gl.message.sender_address)
    self.error = "None"

@gl.public.write
def add_admin(self, admin_contract: str) -> None:
    if self.owner != gl.message.sender_address:
        raise Exception("Not owner")
    self.admins.append(Address(admin_contract))

@gl.public.write
def clear_admins(self) -> None:
    if self.owner != gl.message.sender_address:
        raise Exception("Not owner")
    self.admins.clear()
    self.admins.append(gl.message.sender_address)

@gl.public.write
def add_user_points(self, player_address: str, point: u256) -> None:
    if gl.message.sender_address not in self.admins:
        raise Exception("Not admin")
    pa = Address(player_address)
    if pa not in self.points:
        self.points[pa] = 0
    self.points[pa] += point

@gl.public.write
def add_user_points_by_game(self, player_address: str, game_type: u256, point: u256) -> None:
    if gl.message.sender_address not in self.admins:
        raise Exception("Not admin")
    pa = Address(player_address)
    if pa not in self.points:
        self.points[pa] = 0
    self.points[pa] += point
    pp = self.points_by_game.get_or_insert_default(pa)
    if game_type not in pp:
        pp[game_type] = 0
    self.points_by_game.get(pa)[game_type] += point

@gl.public.write
def add_game_to_archive(self, player_address: str, game_id: str, is_creator: bool, game_time: str, game_type: u256) -> None:
    if gl.message.sender_address not in self.admins:
        raise Exception("Not admin")
    self.games_archive.get_or_insert_default(Address(player_address))[game_id] = GameArchive(
        is_creator=is_creator,
        game_time=game_time,
        game_type=game_type,
        game_id=game_id
    )

@gl.public.write
def add_user_points_game_to_archive(self, player_address: str, game_id: str, game_time: str, game_type: u256, point: u256) -> None:
    if gl.message.sender_address not in self.admins:
        raise Exception("Not admin")
    self.games_archive.get_or_insert_default(Address(player_address))[game_id] = GameArchive(
        is_creator=False,
        game_time=game_time,
        game_type=game_type,
        game_id=game_id
    )
    pa = Address(player_address)
    if pa not in self.points:
        self.points[pa] = 0
    self.points[pa] += point
    pp = self.points_by_game.get_or_insert_default(pa)
    if game_type not in pp:
        pp[game_type] = 0
    self.points_by_game.get(pa)[game_type] += point

@gl.public.write
def set_nickname(self, nick: str) -> None:
    self.nicknames[gl.message.sender_address] = _truncate(nick, 25)

@gl.public.view
def get_nicknames(self) -> dict:
    return {k.as_hex: v for k, v in self.nicknames.items()}

@gl.public.view
def get_my_nickname(self) -> str:
    return self.nicknames.get(gl.message.sender_address, "")

@gl.public.view
def get_points(self, limit: u256) -> str:
    result = []
    for k, v in sorted(self.points.items(), key=lambda kv: float(kv[1]), reverse=True)[:limit]:
        result.append({"wallet": k.as_hex, "nick": self.nicknames.get(k, ""), "points": str(v)})
    return json.dumps(result)

@gl.public.view
def get_my_points(self) -> str:
    pa = gl.message.sender_address
    pts = self.points.get(pa, 0)
    by_game = self.points_by_game.get(pa)
    return json.dumps({
        "wallet": pa.as_hex,
        "nick": self.nicknames.get(pa, ""),
        "points": str(pts),
        "points_by_game": [{"game_type": str(k), "points": str(v)} for k, v in by_game.items()] if by_game else []
    })

@gl.public.view
def get_all_my_archive(self, limit: u256) -> str:
    games = self.games_archive.get(gl.message.sender_address)
    if games is None:
        return json.dumps([])
    result = []
    for archive in sorted(games.values(), key=lambda x: float(x.game_time), reverse=True)[:limit]:
        result.append(archive.to_dict())
    return json.dumps(result)

@gl.public.view
def get_admins(self) -> str:
    return json.dumps([{"address": a.as_hex} for a in self.admins])

@gl.public.view
def get_error(self) -> str:
    return self.error
```

def _truncate(s: str, n: int) -> str:
return s if len(s) <= n else s[:n] + “…”
