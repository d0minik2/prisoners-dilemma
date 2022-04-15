import strategies
from config import *
from dataclasses import dataclass


class Colony(object):
    """Colony (Prisoner)"""

    strategy: strategies.Strategy

    battle_score: int = 0
    total_battle_score: int = 0
    tournament_score: int = 0

    current_opponent = None
    battle_course = []
    battle_course_results = []

    def __init__(
            self,
            strategy: strategies.StatisticalStrategy
    ):
        self.strategy = strategy(colony=self)

    def __str__(self) -> str:
        return f"Colony, {self.strategy.name} Strategy"

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
    """Leads the course of the battle between 2 colonies"""

    colony1: Colony
    colony2: Colony
    number_of_rounds: int = ROUNDS
    battle_course = []

    def get_round_result(self) -> tuple[int, int]:
        """Returns a result of the battle for 2 colonies (colony1, colony2)"""

        return SCORES[self.colony2.get_strategy()][self.colony1.get_strategy()]

    def get_battle_result(self) -> Colony or None:
        """Leads the battle course and returns the result (result is the winning colony or None if it is a tie)"""

        self.colony1.new_battle(self.colony2)
        self.colony2.new_battle(self.colony1)

        for _ in range(self.number_of_rounds):
            result = self.get_round_result()
            self.battle_course.append(result)

            self.colony1.submit_round_result(result[0])
            self.colony2.submit_round_result(result[1])

        if self.colony1.battle_score > self.colony2.battle_score:
            return self.colony1
        elif self.colony1.battle_score < self.colony2.battle_score:
            return self.colony2
        return None  # if it is a tie
