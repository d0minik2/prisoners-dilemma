from __future__ import annotations
from abc import ABC, abstractmethod
from random import randint
from dataclasses import dataclass


class Strategy(ABC):
    """Strategy for a battle"""

    name: str
    colony: Colony

    @abstractmethod
    def get_choice(self) -> int:
        """Returns a choice for current round"""


@dataclass
class RandomStrategy(Strategy):
    """Choice of that strategy is random"""

    name = "Random"
    colony: Colony

    def get_choice(self) -> int:
        return randint(0, 1)


@dataclass
class AlwaysZeroStrategy(Strategy):
    """Choice of that strategy is always 0"""

    name = "Always Zero"
    colony: Colony

    def get_choice(self) -> int:
        return 0


@dataclass
class AlwaysOneStrategy(Strategy):
    """Choice of that strategy is always 1"""

    name = "Always One"
    colony: Colony

    def get_choice(self) -> int:
        return 1


@dataclass
class StatisticalStrategy(Strategy):
    """Choice of that strategy is the most winning choice in current battle"""

    name = "Statistical"
    colony: Colony

    def get_choice(self) -> int:
        battle_course = self.colony.battle_course
        battle_course_results = self.colony.battle_course_results

        assert battle_course is not None, "Battle course not found"
        assert battle_course_results is not None, "Battle course results not found"

        if len(battle_course) >= 2:
            confess_score, defend_score = 0, 0

            for i in range(len(battle_course_results)):
                if battle_course[i] == 0:
                    confess_score += battle_course_results[i-1]

                elif battle_course[i] == 1:
                    defend_score += battle_course_results[i-1]

            try:
                confess_score, defend_score = confess_score / battle_course.count(0), defend_score / battle_course.count(1)

                if confess_score > defend_score:
                    return 0
                elif confess_score < defend_score:
                    return 1
                else:
                    return randint(0, 1)

            except ZeroDivisionError:
                return randint(0, 1)

        return 0


@dataclass
class WeirdStrategy(Strategy):
    """Choice of that strategy is always diffrent than the last choice"""

    name = "Wierd"
    colony: Colony

    def get_choice(self) -> int:
        battle_course = self.colony.battle_course

        assert battle_course is not None, "Battle course not found"

        if len(battle_course) >= 1:
            return int(not battle_course[-1])
        else:
            return randint(0, 1)


@dataclass
class OpponentsLastStrategy(Strategy):
    """Returns the opponent's last choice"""

    name = "Opponent's Last"
    colony: Colony

    def get_choice(self) -> int:
        opponents_battle_course = self.colony.current_opponent.battle_course

        assert opponents_battle_course is not None, "Opponent's battle course not found"

        if opponents_battle_course:
            return opponents_battle_course[-1]
        else:
            return 1


@dataclass
class HackerStrategy(Strategy):
    """Returns the best choice"""

    name = "Hacker"
    colony: Colony

    def get_choice(self) -> int:
        opponents_strategy = self.colony.current_opponent.strategy

        assert opponents_strategy is not None, "Opponent's strategy not found"

        if isinstance(opponents_strategy, HackerStrategy):
            return opponents_strategy.get_choice()
        return 0