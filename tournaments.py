from dataclasses import dataclass
import colonies
from strategies import *
import random
from abc import ABC, abstractmethod
import numpy as np


class Tournament(ABC):
    """Colony tournament"""

    alive: list
    ranking: list

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

    alive: list
    result_function = None
    ranking = []

    def get_winner(self):
        if not len(self.ranking):
            return self.start()[0]
        return self.ranking[0]

    def get_result(self) -> list[colonies.Colony]:
        if not len(self.ranking):
            return self.start()
        return self.ranking

    def start(self) -> list[colonies.Colony]:
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

    alive: list
    ranking = []
    result_function = None

    points_for_winning = 2
    points_for_tie = 1
    points_for_loose = 0

    def get_winner(self):
        if not len(self.ranking):
            return self.start()[0]
        return self.ranking[0]

    def get_result(self) -> list[colonies.Colony]:
        if not len(self.ranking):
            return self.start()
        return self.ranking

    def start(self) -> list[colonies.Colony]:
        pairings = []

        for colony1 in range(len(self.alive)):
            for colony2 in range(colony1 + 1, len(self.alive)):
                pairings.append((self.alive[colony1], self.alive[colony2]))

        for colony1, colony2 in pairings:
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

        self.ranking = list(sorted(
            self.alive,
            key=lambda colony: colony.tournament_score,
            reverse=True
        ))
        return self.ranking


@dataclass
class PopulationGrowTournament(Tournament):
    """Tournament where colonies grow, the larger population, the greater chance of fighting.
    Population is the total battle score"""

    alive: list
    ranking = []
    round_history = {}
    result_function = None
    rounds: int = 1000

    def get_winner(self):
        if not len(self.ranking):
            self.start()
        return self.ranking[0]

    def get_result(self) -> dict[int, tuple[colonies.Colony, list[int]]]:
        if not self.round_history:
            return self.start()
        return self.round_history

    def choose_colonies_to_fight(self) -> (colonies.Colony, colonies.Colony):
        weights = [max(colony.total_battle_score, 1) for colony in self.alive]

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

    def start(self) -> dict[int, tuple[colonies.Colony, list[int]]]:
        for colony in self.alive:
            if self.round_history.get(id(colony)) is None:
                self.round_history[id(colony)] = (colony, [])

        current_round = 0

        while current_round <= self.rounds and len(self.alive) > 1:
            current_round += 1

            colony1, colony2 = self.choose_colonies_to_fight()

            battle = colonies.Battle(
                colony1=colony1,
                colony2=colony2
            )
            battle_result = battle.get_battle_result()

            for colony_id, colony in self.round_history.items():
                self.round_history[colony_id][1].append(colony[0].total_battle_score)

        self.ranking = sorted(
            self.alive,
            key=lambda colony: colony.total_battle_score,
            reverse=True
        )
        return self.round_history


if __name__ == "__main__":
    # creating example tournament

    players = [
        colonies.Colony(StatisticalStrategy),
        colonies.Colony(WeirdStrategy),
        colonies.Colony(HackerStrategy),
        colonies.Colony(RandomStrategy),
        colonies.Colony(AlwaysZeroStrategy),
        colonies.Colony(AlwaysOneStrategy),
        colonies.Colony(OpponentsLastStrategy)
    ]

    tournament = LeagueTournament(alive=players)
    tournament.start()
    print(tournament.get_winner())
    print(tournament.get_result())