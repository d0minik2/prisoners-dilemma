import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

from config import *
import strategies
from dataclasses import dataclass



class Prisoner(object):
    """Prisoner"""

    strategy: strategies.Strategy

    battle_score: int = 0
    total_battle_score: int = 0
    tournament_score: int = 0

    current_opponent = None
    battle_course = []
    battle_course_results = []

    def __init__(
            self,
            strategy: object
    ):
        self.strategy = strategy(prisoner=self)

    def __repr__(self):
        return f"Prisoner({self.strategy.name} Strategy)"

    def get_strategy(self) -> int:
        """Returns a strategy choice (0 or 1)"""

        choice = self.strategy.get_choice()

        self.battle_course.append(choice)
        return choice

    def new_battle(self, opponent) -> None:
        """Resets the results of the last battle"""

        self.battle_course.clear()
        self.battle_course_results.clear()
        self.current_opponent = opponent
        self.battle_score = 0

    def submit_round_result(self, result: int) -> None:
        """Submits the scores after the round in a battle"""

        self.battle_score += result
        self.total_battle_score += result
        self.battle_course_results.append(result)


@dataclass
class Battle(object):
    """Leads the course of the battle between 2 prisoners"""

    prisoner1: Prisoner
    prisoner2: Prisoner
    number_of_rounds: int = ROUNDS
    battle_course = []

    def get_round_result(self) -> tuple[int, int]:
        """Returns a result of the battle for 2 prisoners (prisoner1, prisoner2)"""

        return SCORES[self.prisoner2.get_strategy()][self.prisoner1.get_strategy()]

    def get_battle_result(self) -> Prisoner or None:
        """Leads the battle course and returns the result (result is the winning prisoner or None if it is a tie)"""

        self.prisoner1.new_battle(self.prisoner2)
        self.prisoner2.new_battle(self.prisoner1)

        for _ in range(self.number_of_rounds):
            result = self.get_round_result()
            self.battle_course.append(result)

            self.prisoner1.submit_round_result(result[0])
            self.prisoner2.submit_round_result(result[1])

        if self.prisoner1.battle_score > self.prisoner2.battle_score:
            return self.prisoner1
        elif self.prisoner1.battle_score < self.prisoner2.battle_score:
            return self.prisoner2
        return None  # if it is a tie
