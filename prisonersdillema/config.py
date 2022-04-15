#### BattleRules

# number of rounds for each battle
ROUNDS = 10

SCORES = (((0, 0), (0, 2)),
          ((2, 0), (1, 1)))
# table of scores
#
#                 p1:         <- player 1
#             0         1      <- player's 1 choice
# p2:  0  ((s1, s2), (s1, s2))
#      1  ((s1, s2), (s1, s2))
#      ^
#      | player's 2 choice
#
# s1 - score for player 1
# s2 - score for player 2
