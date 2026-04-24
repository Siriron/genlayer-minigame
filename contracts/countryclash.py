
# { “Depends”: “py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6” }

from genlayer import *
from dataclasses import dataclass
from datetime import datetime, timezone
import typing
import json

@gl.contract_interface
class StatIface:
class View:
def get_nicknames(self) -> dict: …
class Write:
def add_user_points_by_game(self, player_address: str, game_type: u256, point: u256) -> None: …
def add_user_points_game_to_archive(self, player_address: str, game_id: str, game_time: str, game_type: u256, point: u256) -> None: …
def add_game_to_archive(self, player_address: str, game_id: str, is_creator: bool, game_time: str, game_type: u256) -> None: …

@gl.contract_interface
class StorageIface:
class View:
def get_round(self, round_id: str) -> dict: …
class Write:
def add_round(self, round: dict) -> None: …

@allow_storage
@dataclass
class Round:
round_id: str
player: Address
country_a: str
country_b: str
metric: str
correct_answer: str
player_answer: str
score: u256
game_time: str
is_correct: bool

```
def __init__(self, round_id: str, player: Address):
    self.round_id = round_id
    self.player = player
    self.is_correct = False

def to_dict(self):
    return {
        "round_id": self.round_id,
        "player": self.player.as_hex,
        "country_a": self.country_a,
        "country_b": self.country_b,
        "metric": self.metric,
        "correct_answer": self.correct_answer,
        "player_answer": self.player_answer,
        "score": str(self.score),
        "game_time": self.game_time,
        "is_correct": str(self.is_correct)
    }
```

METRICS = [“GDP”, “population”, “area”, “life expectancy”, “inflation rate”]
GAME_TYPE = 5

class CountryClash(gl.Contract):
owner: Address
stat: Address
storage: Address
base_score: u256
error: str
active_rounds: TreeMap[Address, Round]

```
def __init__(self, stat_contract: str, storage_contract: str) -> None:
    self.owner = gl.message.sender_address
    self.stat = Address(stat_contract)
    self.storage = Address(storage_contract)
    self.base_score = 100
    self.error = "None"

@gl.public.write
def add_stat_contract(self, stat_contract: str) -> None:
    if self.owner != gl.message.sender_address:
        raise Exception("Not owner")
    self.stat = Address(stat_contract)

@gl.public.write
def add_storage_contract(self, storage_contract: str) -> None:
    if self.owner != gl.message.sender_address:
        raise Exception("Not owner")
    self.storage = Address(storage_contract)

@gl.public.write
def set_base_score(self, score: int) -> None:
    if self.owner != gl.message.sender_address:
        raise Exception("Not owner")
    self.base_score = score

@gl.public.write
def start_round(self, round_id: str, country_a: str, country_b: str, metric: str) -> typing.Any:
    sender = gl.message.sender_address
    time_str = gl.message_raw["datetime"]
    t = _convert_time(time_str)

    existing = self.active_rounds.get(sender)
    if existing is not None:
        StorageIface(self.storage).emit().add_round(existing.to_dict())

    def fetch_countries():
        url_a = f"https://restcountries.com/v3.1/name/{country_a}?fullText=true"
        url_b = f"https://restcountries.com/v3.1/name/{country_b}?fullText=true"
        data_a = gl.nondet.web.get(url_a).body.decode("utf-8")
        data_b = gl.nondet.web.get(url_b).body.decode("utf-8")
        prompt = f"""
```

You are given two countries and a metric. Determine which country ranks HIGHER on that metric.

Country A: {country_a}
Country B: {country_b}
Metric: {metric}

Raw data for Country A: {data_a[:1000]}
Raw data for Country B: {data_b[:1000]}

Based on this data and your knowledge, which country has the HIGHER {metric}?
Respond with ONLY the country name exactly as given: either “{country_a}” or “{country_b}”.
No explanation. Just the name.
“””
return gl.nondet.exec_prompt(prompt)

```
    try:
        result = gl.eq_principle.strict_eq(fetch_countries)
        correct = result.splitlines()[0].strip()

        round_obj = Round(round_id=round_id, player=sender)
        round_obj.country_a = country_a
        round_obj.country_b = country_b
        round_obj.metric = metric
        round_obj.correct_answer = correct
        round_obj.player_answer = ""
        round_obj.score = 0
        round_obj.game_time = t
        round_obj.is_correct = False

        self.active_rounds[sender] = round_obj
        StatIface(self.stat).emit().add_game_to_archive(sender.as_hex, round_id, True, t, GAME_TYPE)
        self.error = f"Round started: {country_a} vs {country_b} on {metric}"
    except Exception as e:
        self.error = "start_round error: " + str(e)

@gl.public.write
def submit_answer(self, round_id: str, player_answer: str, elapsed_seconds: int) -> typing.Any:
    sender = gl.message.sender_address
    time_str = gl.message_raw["datetime"]
    t = _convert_time(time_str)

    round_obj = self.active_rounds.get(sender)
    if round_obj is None:
        self.error = "No active round"
        return
    if round_obj.round_id != round_id:
        self.error = "Round ID mismatch"
        return

    try:
        is_correct = player_answer.strip().lower() == round_obj.correct_answer.strip().lower()
        speed_bonus = max(0.1, 1.0 - (elapsed_seconds / 30.0))
        score = int(self.base_score * speed_bonus) if is_correct else 0

        round_obj.player_answer = player_answer
        round_obj.score = score
        round_obj.is_correct = is_correct

        self.active_rounds[sender] = round_obj

        if is_correct and score > 0:
            StatIface(self.stat).emit().add_user_points_game_to_archive(
                sender.as_hex, round_id, t, GAME_TYPE, score
            )

        StorageIface(self.storage).emit().add_round(round_obj.to_dict())
        del self.active_rounds[sender]
        self.error = f"Answered: {player_answer} | Correct: {round_obj.correct_answer} | Score: {score}"
    except Exception as e:
        self.error = "submit_answer error: " + str(e)

@gl.public.view
def get_active_round(self) -> str:
    sender = gl.message.sender_address
    round_obj = self.active_rounds.get(sender)
    if round_obj is None:
        return json.dumps({"error": "No active round"})
    return json.dumps({
        "round_id": round_obj.round_id,
        "country_a": round_obj.country_a,
        "country_b": round_obj.country_b,
        "metric": round_obj.metric,
        "game_time": round_obj.game_time
    })

@gl.public.view
def get_base_score(self) -> int:
    return int(self.base_score)

@gl.public.view
def get_error(self) -> str:
    return self.error
```

def _convert_time(time_str: str) -> str:
dt = datetime.strptime(time_str, “%Y-%m-%dT%H:%M:%S.%fZ”).replace(tzinfo=timezone.utc)
return str(dt.timestamp())
