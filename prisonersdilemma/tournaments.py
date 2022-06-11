import prisoners
from strategies import *

import random
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Generator, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Tournament:
    """Prisoners tournament"""

    alive: List[prisoners.Prisoner]
    ranking: sorted

    def get_winner(self) -> prisoners.Prisoner:
        """Returns a winner of the Tournament"""

    def get_result(self) -> list[prisoners.Prisoner]:
        """Returns a result of the Tournament"""

    def start(self) -> list[prisoners.Prisoner]:
        """Runs the tournament and returns its result"""

    def show_result(self) -> None:
        if not self.ranking:
            return self.start()

        try:
            self.show()
        except AttributeError:
            print(f"Winner: {self.get_winner()}")
            print(f"Result: {self.get_result()}")


@dataclass
class SingleEliminationTournament(Tournament):
    """Single Elimination Tournament"""

    alive: List[prisoners.Prisoner]
    ranking = sorted([], reverse=True)

    def get_winner(self) -> prisoners.Prisoner:
        if not len(self.ranking):
            return self.start()[0]
        return self.ranking[0]

    def get_result(self) -> List[prisoners.Prisoner]:
        if not len(self.ranking):
            return self.start()
        return self.ranking

    def start(self) -> List[prisoners.Prisoner]:
        random.shuffle(self.alive)

        for prisoner1, prisoner2 in zip(
            self.alive[:len(self.alive) // 2],
            self.alive[len(self.alive) // 2:]
        ):

            battle = prisoners.Battle(
                prisoner1=prisoner1,
                prisoner2=prisoner2
            )
            battle_result = battle.get_battle_result()

            if battle_result is not None:
                if battle_result == prisoner1:
                    self.ranking.append(prisoner2)
                    self.alive.remove(prisoner2)
                else:
                    self.ranking.append(prisoner1)
                    self.alive.remove(prisoner1)
            else:
                if len(self.alive) <= 2:
                    winners = [prisoner1, prisoner2]
                    random.shuffle(winners)

                    for prisoner in winners:
                        self.ranking.append(prisoner)
                        self.alive.remove(prisoner)

        if len(self.alive) > 1:
            self.start()
        self.ranking = list(reversed(self.ranking))
        return self.ranking


@dataclass
class LeagueTournament(Tournament):
    """Tournament where every prisoner fights against every prisoner"""

    alive: List[prisoners.Prisoner]
    ranking = sorted([], reverse=True)

    points_for_winning = 2
    points_for_tie = 1
    points_for_loose = 0

    def get_winner(self) -> prisoners.Prisoner:
        if not len(self.ranking):
            return self.start()[0]
        return self.ranking[0]

    def get_result(self) -> list[prisoners.Prisoner]:
        if not len(self.ranking):
            return self.start()
        return self.ranking

    def pair_players(self) -> Generator[Tuple[prisoners.Prisoner, prisoners.Prisoner], None, None]:
        for prisoner1_idx, prisoner1 in enumerate(self.alive):
            for prisoner2 in self.alive[prisoner1_idx + 1:]:
                yield prisoner1, prisoner2

    def start(self) -> list[prisoners.Prisoner]:
        for prisoner1, prisoner2 in self.pair_players():
            battle = prisoners.Battle(
                prisoner1=prisoner1,
                prisoner2=prisoner2
            )

            if (battle_result := battle.get_battle_result()) is not None:
                if battle_result == prisoner1:
                    prisoner1.tournament_score += self.points_for_winning
                    prisoner2.tournament_score += self.points_for_loose
                else:
                    prisoner2.tournament_score += self.points_for_winning
                    prisoner1.tournament_score += self.points_for_loose
            else:
                prisoner1.tournament_score += self.points_for_tie
                prisoner2.tournament_score += self.points_for_tie

        self.ranking = sorted(
            self.alive,
            key=lambda prisoner: prisoner.tournament_score,
            reverse=True
        )
        return self.ranking


@dataclass
class PrisonerStrengthenTournament(Tournament):
    """Tournament where prisoner are getting stronger, the larger total_battle_score, the greater chance of fighting."""

    alive: List[prisoners.Prisoner]
    ranking = sorted([], reverse=True)

    tournament_course = pd.DataFrame()
    rounds: int = 1000

    def get_winner(self) -> prisoners.Prisoner:
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
        plt.legend(loc="upper left")
        plt.show()


    def choose_prisoners_to_fight(self) -> (prisoners.Prisoner, prisoners.Prisoner):
        weights = [max(prisoner.total_battle_score//2, 1) for prisoner in self.alive]

        prisoner1, prisoner2 = random.choices(
            self.alive,
            weights=weights,
            k=2
        )

        while prisoner1 is prisoner2:
            prisoner2 = random.choices(
                self.alive,
                weights=weights,
                k=1
            )[0]

        return prisoner1, prisoner2

    def start(self) -> pd.DataFrame:

        self.tournament_course = pd.DataFrame({prisoner: np.zeros(self.rounds) for prisoner in self.alive})
        current_round = 0

        while current_round < self.rounds and len(self.alive) > 1:
            current_round += 1

            prisoner1, prisoner2 = self.choose_prisoners_to_fight()

            battle = prisoners.Battle(
                prisoner1=prisoner1,
                prisoner2=prisoner2
            )
            battle_result = battle.get_battle_result()

            self.tournament_course.values[current_round-1] = pd.DataFrame(
                {prisoner: [prisoner.total_battle_score] for prisoner in self.tournament_course}
            )

        self.ranking = sorted(
            self.alive,
            key=lambda prisoner: prisoner.total_battle_score,
            reverse=True
        )
        return self.tournament_course
