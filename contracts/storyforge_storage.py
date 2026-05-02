# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
from dataclasses import dataclass
from itertools import islice
import typing
import json

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

class StoryForgeStorage(gl.Contract):
    owner: Address
    admins: DynArray[Address]
    rounds: TreeMap[str, Round]
    error: str

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
    def add_round(self, round: dict) -> typing.Any:
        if gl.message.sender_address not in self.admins:
            raise Exception("Not admin")
        round_id = round.get("round_id")
        if round_id in self.rounds:
            self.error = "Round exists: " + round_id
            return
        try:
            r = Round(round_id=round_id, player=Address(round.get("player")))
            r.topic = round.get("topic", "")
            r.headline = round.get("headline", "")
            r.player_ending = round.get("player_ending", "")
            r.score = int(round.get("score", 0))
            r.game_time = round.get("game_time", "")
            r.feedback = round.get("feedback", "")
            self.rounds[round_id] = r
            self.error = "Round added: " + round_id
        except Exception as e:
            self.error = "add_round error: " + str(e)

    @gl.public.view
    def get_recent_rounds(self, limit: int) -> str:
        try:
            result = []
            for k, v in islice(
                sorted(self.rounds.items(), key=lambda x: float(x[1].game_time), reverse=True),
                limit
            ):
                result.append(v.to_dict())
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @gl.public.view
    def get_admins(self) -> str:
        return json.dumps([{"address": a.as_hex} for a in self.admins])

    @gl.public.view
    def get_error(self) -> str:
        return self.error
