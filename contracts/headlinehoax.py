# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
from dataclasses import dataclass
from datetime import datetime, timezone
import typing
import json

@gl.contract_interface
class StatIface:
    class View:
        def get_nicknames(self) -> dict: ...
    class Write:
        def add_user_points_by_game(self, player_address: str, game_type: u256, point: u256) -> None: ...
        def add_user_points_game_to_archive(self, player_address: str, game_id: str, game_time: str, game_type: u256, point: u256) -> None: ...
        def add_game_to_archive(self, player_address: str, game_id: str, is_creator: bool, game_time: str, game_type: u256) -> None: ...

@gl.contract_interface
class StorageIface:
    class View:
        def get_round(self, round_id: str) -> dict: ...
    class Write:
        def add_round(self, round: dict) -> None: ...

@allow_storage
@dataclass
class Round:
    round_id: str
    player: Address
    topic: str
    real_headline: str
    fake_headline: str
    correct_answer: str
    player_answer: str
    score: u256
    game_time: str
    is_correct: bool

    def __init__(self, round_id: str, player: Address):
        self.round_id = round_id
        self.player = player
        self.is_correct = False

    def to_dict(self):
        return {
            "round_id": self.round_id,
            "player": self.player.as_hex,
            "topic": self.topic,
            "real_headline": self.real_headline,
            "fake_headline": self.fake_headline,
            "correct_answer": self.correct_answer,
            "player_answer": self.player_answer,
            "score": str(self.score),
            "game_time": self.game_time,
            "is_correct": str(self.is_correct)
        }

GAME_TYPE = 6

class HeadlineHoax(gl.Contract):
    owner: Address
    stat: Address
    storage: Address
    base_score: u256
    error: str
    active_rounds: TreeMap[Address, Round]

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
    def start_round(self, round_id: str, topic: str) -> typing.Any:
        sender = gl.message.sender_address
        time_str = gl.message_raw["datetime"]
        t = _convert_time(time_str)

        existing = self.active_rounds.get(sender)
        if existing is not None:
            StorageIface(self.storage).emit().add_round(existing.to_dict())

        def fetch_and_generate():
            topic_queries = {
                "World News": "https://newsapi.org/v2/top-headlines?category=general&pageSize=5&apiKey=demo",
                "Tech": "https://newsapi.org/v2/top-headlines?category=technology&pageSize=5&apiKey=demo",
                "Crypto": "https://newsapi.org/v2/everything?q=cryptocurrency+bitcoin&sortBy=publishedAt&pageSize=5&apiKey=demo",
                "Science": "https://newsapi.org/v2/top-headlines?category=science&pageSize=5&apiKey=demo",
                "Sports": "https://newsapi.org/v2/top-headlines?category=sports&pageSize=5&apiKey=demo",
            }
            search_url = f"https://hn.algolia.com/api/v1/search_by_date?query={topic}&tags=story&hitsPerPage=10"
            raw = gl.nondet.web.get(search_url).body.decode("utf-8")

            prompt = f"""
You are a news headline game master. Your job is to create a challenging and fun game round.

Topic: {topic}
Recent news data: {raw[:2000]}

Instructions:
1. Extract ONE real, recent headline from the data above. It must be a genuine headline.
2. Create ONE convincing fake headline on the same topic. It should sound plausible but be fabricated.
3. The fake headline should be similar in style and length to the real one.

Respond in this exact format (no extra text):
REAL: [the real headline here]
FAKE: [the fake headline here]
"""
            return gl.nondet.exec_prompt(prompt)

        try:
            result = gl.eq_principle.strict_eq(fetch_and_generate)
            lines = result.strip().splitlines()
            real_headline = ""
            fake_headline = ""
            for line in lines:
                if line.startswith("REAL:"):
                    real_headline = line[5:].strip()
                elif line.startswith("FAKE:"):
                    fake_headline = line[5:].strip()

            if not real_headline or not fake_headline:
                self.error = "Failed to parse headlines"
                return

            round_obj = Round(round_id=round_id, player=sender)
            round_obj.topic = topic
            round_obj.real_headline = real_headline
            round_obj.fake_headline = fake_headline
            round_obj.correct_answer = "REAL"
            round_obj.player_answer = ""
            round_obj.score = 0
            round_obj.game_time = t
            round_obj.is_correct = False

            self.active_rounds[sender] = round_obj
            StatIface(self.stat).emit().add_game_to_archive(sender.as_hex, round_id, True, t, GAME_TYPE)
            self.error = f"Round started: {topic}"
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
            is_correct = player_answer.strip().upper() == "REAL"
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
            self.error = f"Answered: {player_answer} | Correct: REAL | Score: {score}"
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
            "topic": round_obj.topic,
            "real_headline": round_obj.real_headline,
            "fake_headline": round_obj.fake_headline,
            "game_time": round_obj.game_time
        })

    @gl.public.view
    def get_base_score(self) -> int:
        return int(self.base_score)

    @gl.public.view
    def get_error(self) -> str:
        return self.error

def _convert_time(time_str: str) -> str:
    dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return str(dt.timestamp())
