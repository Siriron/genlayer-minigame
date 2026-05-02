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
    class Write:
        def add_round(self, round: dict) -> None: ...

@allow_storage
@dataclass
class Round:
    round_id: str
    player: Address
    topic: str
    headline: str
    player_ending: str
    score: u256
    game_time: str
    feedback: str

    def __init__(self, round_id: str, player: Address):
        self.round_id = round_id
        self.player = player
        self.score = 0
        self.feedback = ""

    def to_dict(self):
        return {
            "round_id": self.round_id,
            "player": self.player.as_hex,
            "topic": self.topic,
            "headline": self.headline,
            "player_ending": self.player_ending,
            "score": str(self.score),
            "game_time": self.game_time,
            "feedback": self.feedback
        }

GAME_TYPE = 7

TOPIC_URLS = {
    "World": "https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=10",
    "Tech": "https://hn.algolia.com/api/v1/search_by_date?query=technology+software&tags=story&hitsPerPage=10",
    "Science": "https://hn.algolia.com/api/v1/search_by_date?query=science+research&tags=story&hitsPerPage=10",
    "Crypto": "https://hn.algolia.com/api/v1/search_by_date?query=bitcoin+crypto&tags=story&hitsPerPage=10",
    "Business": "https://hn.algolia.com/api/v1/search_by_date?query=business+startup+economy&tags=story&hitsPerPage=10",
}

class StoryForge(gl.Contract):
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
    def start_round(self, round_id: str, topic: str) -> typing.Any:
        sender = gl.message.sender_address
        time_str = gl.message_raw["datetime"]
        t = _convert_time(time_str)

        existing = self.active_rounds.get(sender)
        if existing is not None:
            StorageIface(self.storage).emit().add_round(existing.to_dict())

        url = TOPIC_URLS.get(topic, TOPIC_URLS["World"])

        def fetch_story():
            raw = gl.nondet.web.get(url).body.decode("utf-8")
            prompt = f"""You are a news story game master.

Topic: {topic}
HackerNews data: {raw[:3000]}

From the data above, pick ONE interesting recent news story.
Extract its headline and write a 1-2 sentence intro that sets up the story WITHOUT revealing the outcome.
The intro should end with suspense — the reader should want to know what happened next.

Respond in EXACTLY this format:
HEADLINE: [the headline]
INTRO: [1-2 sentence story setup without the ending]"""
            return gl.nondet.exec_prompt(prompt)

        try:
            result = gl.eq_principle.strict_eq(fetch_story)
            headline = ""
            intro = ""
            for line in result.strip().splitlines():
                if line.startswith("HEADLINE:"):
                    headline = line[9:].strip()
                elif line.startswith("INTRO:"):
                    intro = line[6:].strip()

            if not headline or not intro:
                self.error = "parse_error: " + result[:100]
                return

            round_obj = Round(round_id=round_id, player=sender)
            round_obj.topic = topic
            round_obj.headline = headline
            round_obj.player_ending = ""
            round_obj.score = 0
            round_obj.game_time = t
            round_obj.feedback = ""

            self.active_rounds[sender] = round_obj
            StatIface(self.stat).emit().add_game_to_archive(sender.as_hex, round_id, True, t, GAME_TYPE)
            self.error = f"Story:{headline}||Intro:{intro}"
        except Exception as e:
            self.error = "start_round error: " + str(e)

    @gl.public.write
    def submit_ending(self, round_id: str, player_ending: str) -> typing.Any:
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

        headline = round_obj.headline

        def evaluate_ending():
            search_url = f"https://hn.algolia.com/api/v1/search?query={headline[:50]}&tags=story&hitsPerPage=5"
            raw = gl.nondet.web.get(search_url).body.decode("utf-8")
            prompt = f"""You are judging a news story completion game.

Original headline: {headline}
Player's ending: {player_ending}
Real story data from web: {raw[:2000]}

Score the player's ending from 0 to 100 based on:
- Accuracy: how close is it to what actually happened? (60 points)
- Creativity: is it well-written and engaging? (40 points)

Respond in EXACTLY this format:
SCORE: [number 0-100]
FEEDBACK: [1-2 sentences explaining the score]"""
            return gl.nondet.exec_prompt(prompt)

        try:
            result = gl.eq_principle.strict_eq(evaluate_ending)
            score = 0
            feedback = ""
            for line in result.strip().splitlines():
                if line.startswith("SCORE:"):
                    try:
                        score = int(line[6:].strip())
                        score = max(0, min(100, score))
                    except:
                        score = 0
                elif line.startswith("FEEDBACK:"):
                    feedback = line[9:].strip()

            round_obj.player_ending = player_ending
            round_obj.score = score
            round_obj.feedback = feedback
            self.active_rounds[sender] = round_obj

            if score > 0:
                StatIface(self.stat).emit().add_user_points_game_to_archive(
                    sender.as_hex, round_id, t, GAME_TYPE, score
                )

            StorageIface(self.storage).emit().add_round(round_obj.to_dict())
            del self.active_rounds[sender]
            self.error = f"Result:Score:{score}||Feedback:{feedback}"
        except Exception as e:
            self.error = "submit_ending error: " + str(e)

    @gl.public.view
    def get_error(self) -> str:
        return self.error

    @gl.public.view
    def get_base_score(self) -> int:
        return int(self.base_score)

def _convert_time(time_str: str) -> str:
    dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return str(dt.timestamp())
