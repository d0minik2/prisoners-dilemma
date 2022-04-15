
import colonies
from strategies import *

import random
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Generator, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Tournament(ABC):
    """Colony tournament"""

    alive: List[colonies.Colony]
    ranking: sorted

    @abstractmethod
    def get_winner(self) -> colonies.Colony:
        """Returns a winner of the Tournament"""

    @abstractmethod
    def get_result(self) -> list[colonies.Colony]:
        """Returns a result of the Tournament"""

    @abstractmethod
    def start(self) -> list[colonies.Colony]:
        """Runs the tournament and returns its result"""


@dataclass
class SingleEliminationTournament(Tournament):
    """Single Elimination Tournament"""

    alive: List[colonies.Colony]
    ranking = sorted([], reverse=True)

    def get_winner(self) -> colonies.Colony:
        if not len(self.ranking):
            return self.start()[0]
        return self.ranking[0]

    def get_result(self) -> List[colonies.Colony]:
        if not len(self.ranking):
            return self.start()
        return self.ranking

    def start(self) -> List[colonies.Colony]:
        random.shuffle(self.alive)

        for colony1, colony2 in zip(
            self.alive[:len(self.alive) // 2],
            self.alive[len(self.alive) // 2:]
        ):

            battle = colonies.Battle(
                colony1=colony1,
                colony2=colony2
            )
            battle_result = battle.get_battle_result()

            if battle_result is not None:
                if battle_result == colony1:
                    self.ranking.append(colony2)
                    self.alive.remove(colony2)
                else:
                    self.ranking.append(colony1)
                    self.alive.remove(colony1)
            else:
                if len(self.alive) <= 2:
                    winners = [colony1, colony2]
                    random.shuffle(winners)

                    for colony in winners:
                        self.ranking.append(colony)
                        self.alive.remove(colony)

        if len(self.alive) > 1:
            self.start()
        self.ranking = list(reversed(self.ranking))
        return self.ranking


@dataclass
class LeagueTournament(Tournament):
    """Tournament where every colony fights against every colony"""

    alive: List[colonies.Colony]
    ranking = sorted([], reverse=True)

    points_for_winning = 2
    points_for_tie = 1
    points_for_loose = 0

    def get_winner(self) -> colonies.Colony:
        if not len(self.ranking):
            return self.start()[0]
        return self.ranking[0]

    def get_result(self) -> list[colonies.Colony]:
        if not len(self.ranking):
            return self.start()
        return self.ranking

    def pair_players(self) -> Generator[Tuple[colonies.Colony, colonies.Colony], None, None]:
        for colony1_idx, colony1 in enumerate(self.alive):
            for colony2 in self.alive[colony1_idx + 1:]:
                yield colony1, colony2

    def start(self) -> list[colonies.Colony]:
        for colony1, colony2 in self.pair_players():
            battle = colonies.Battle(
                colony1=colony1,
                colony2=colony2
            )

            if (battle_result := battle.get_battle_result()) is not None:
                if battle_result == colony1:
                    colony1.tournament_score += self.points_for_winning
                    colony2.tournament_score += self.points_for_loose
                else:
                    colony2.tournament_score += self.points_for_winning
                    colony1.tournament_score += self.points_for_loose
            else:
                colony1.tournament_score += self.points_for_tie
                colony2.tournament_score += self.points_for_tie

        self.ranking = sorted(
            self.alive,
            key=lambda colony: colony.tournament_score,
            reverse=True
        )
        return self.ranking


@dataclass
class PopulationGrowTournament(Tournament):
    """Tournament where colonies grow, the larger population, the greater chance of fighting.
    Population is the total battle score"""

    alive: List[colonies.Colony]
    ranking = sorted([], reverse=True)

    tournament_course = pd.DataFrame()
    rounds: int = 1000

    def get_winner(self) -> colonies.Colony:
        if self.tournament_course.empty:
            self.start()

        return self.ranking[0]

    def get_result(self) -> pd.DataFrame:
        if self.tournament_course.empty:
            return self.start()

        return self.tournament_course

    def show(self) -> None:
        if self.tournament_course.empty:
            self.start()

        self.tournament_course.plot.area()
        plt.show()


    def choose_colonies_to_fight(self) -> (colonies.Colony, colonies.Colony):
        weights = [max(colony.total_battle_score//2, 1) for colony in self.alive]

        colony1, colony2 = random.choices(
            self.alive,
            weights=weights,
            k=2
        )

        while colony1 == colony2:
            colony2 = random.choices(
                self.alive,
                weights=weights,
                k=1
            )[0]

        return colony1, colony2

    def start(self) -> pd.DataFrame:

        self.tournament_course = pd.DataFrame({colony: np.zeros(self.rounds) for colony in self.alive})
        current_round = 0

        while current_round < self.rounds and len(self.alive) > 1:
            current_round += 1

            colony1, colony2 = self.choose_colonies_to_fight()

            battle = colonies.Battle(
                colony1=colony1,
                colony2=colony2
            )
            battle_result = battle.get_battle_result()

            self.tournament_course.values[current_round-1] = pd.DataFrame(
                {colony: [colony.total_battle_score] for colony in self.tournament_course}
            )

        self.ranking = sorted(
            self.alive,
            key=lambda colony: colony.total_battle_score,
            reverse=True
        )
        return self.tournament_course




def test():
    """example tournament"""
    players = [
        colonies.Colony(StatisticalStrategy),
        colonies.Colony(WeirdStrategy),
        colonies.Colony(HackerStrategy),
        colonies.Colony(RandomStrategy),
        colonies.Colony(AlwaysZeroStrategy),
        colonies.Colony(AlwaysOneStrategy),
        colonies.Colony(OpponentsLastStrategy)
    ]

    tournament = PopulationGrowTournament(alive=players, rounds=1000)
    tournament.start()
    print("winner", tournament.get_winner())
    print("result", tournament.get_result())
    tournament.show()


if __name__ == "__main__":
    test()