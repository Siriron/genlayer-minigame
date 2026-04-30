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

class HeadlineHoaxStorage(gl.Contract):
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
    def clear_admins(self) -> None:
        if self.owner != gl.message.sender_address:
            raise Exception("Not owner")
        self.admins.clear()
        self.admins.append(gl.message.sender_address)

    @gl.public.write
    def add_round(self, round: dict) -> typing.Any:
        if gl.message.sender_address not in self.admins:
            raise Exception("Not admin")
        round_id = round.get("round_id")
        if round_id in self.rounds:
            self.error = "Round already exists: " + round_id
            return
        try:
            r = Round(round_id=round_id, player=Address(round.get("player")))
            r.topic = round.get("topic")
            r.real_headline = round.get("real_headline")
            r.fake_headline = round.get("fake_headline")
            r.correct_answer = round.get("correct_answer")
            r.player_answer = round.get("player_answer")
            r.score = int(round.get("score", 0))
            r.game_time = round.get("game_time")
            r.is_correct = round.get("is_correct") == "True"
            self.rounds[round_id] = r
            self.error = "Round added: " + round_id
        except Exception as e:
            self.error = "add_round error: " + str(e)

    @gl.public.view
    def get_round(self, round_id: str) -> dict:
        r = self.rounds.get(round_id)
        if r is None:
            return {"error": "Round not found"}
        return r.to_dict()

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
