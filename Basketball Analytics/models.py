import pandas as pd
import logging


class Game:
    def __init__(self, game_id, lineups):

        all_players = lineups.loc[(lineups['Game_id'] == game_id) & (lineups['Period'] == 0)][['Person_id', 'Team_id']]
        all_players = all_players.set_index('Person_id')
        for stat in ['off_points', 'def_points', 'poss']:
            all_players[stat] = [0 for i in range(len(all_players))]

        on_players = lineups.loc[(lineups['Game_id'] == game_id) & (lineups['Period'] == 1)][['Person_id', 'Team_id']]
        on_players = on_players.set_index('Person_id')
        for stat in ['off_points', 'def_points', 'poss']:
            on_players[stat] = [0 for i in range(len(on_players))]

        teams = all_players['Team_id'].unique()
        self.all_players = all_players
        self.on_players = on_players
        self.lineups = lineups
        self.scores = dict(zip(teams, [0, 0]))
        self.poss = 0
        self.period = 1
        self.game_id = game_id

    def substitute(self, leaving_player, entering_player):
        # leaving player's team and opposition
        # leave_team = self.all_players.loc[leaving_player, 'Team_id']
        # leave_opp = list(self.scores.keys())
        # leave_opp.remove(leave_team)
        # leave_opp = leave_opp[0]

        # entering player's team and opposition
        # enter_team = self.all_players.loc[entering_player, 'Team_id']
        # enter_opp = list(self.scores.keys())
        # enter_opp.remove(enter_team)
        # enter_opp = enter_opp[0]

        # update leaving player's stats in all_players
        # update_value_off = self.all_players.loc[leaving_player][1] + \
        #                    self.scores[leave_team] - self.on_players.loc[leaving_player][1]
        # update_value_def = self.all_players.loc[leaving_player][2] + \
        #                    self.scores[leave_opp] - self.on_players.loc[leaving_player][2]
        # update_value_poss = self.all_players.loc[leaving_player][3] + \
        #                     self.poss- self.on_players.loc[leaving_player][3]
        #
        # self.all_players.at[leaving_player, 'off_points'] = update_value_off
        # self.all_players.at[leaving_player, 'def_points'] = update_value_def
        # self.all_players.at[leaving_player, 'poss'] = update_value_poss

        update_value_off = self.all_players.loc[leaving_player][1] + \
                           self.on_players.loc[leaving_player][1]
        update_value_def = self.all_players.loc[leaving_player][2] + \
                           self.on_players.loc[leaving_player][2]
        update_value_poss = self.all_players.loc[leaving_player][3] + \
                            self.on_players.loc[leaving_player][3]

        self.all_players.at[leaving_player, 'off_points'] = update_value_off
        self.all_players.at[leaving_player, 'def_points'] = update_value_def
        self.all_players.at[leaving_player, 'poss'] = update_value_poss

        # update entering player's stats on_players
        if entering_player:
            as_list = self.on_players.index.tolist()
            idx = as_list.index(leaving_player)
            as_list[idx] = entering_player
            self.on_players.index = as_list

            self.on_players.at[entering_player, 'off_points'] = 0
            self.on_players.at[entering_player, 'def_points'] = 0
            self.on_players.at[entering_player, 'poss'] = 0

        print(f'    substitution: \n'
              f'        {leaving_player} leaves the game, \n'
              f'        {entering_player} enters the game')

    def new_period(self):
        self.period += 1
        teams = list(self.scores.keys())
        next_on_players = set(self.lineups.loc[(self.lineups['Game_id'] == self.game_id) &
                                          (self.lineups['Period'] == self.period)]['Person_id'].values.tolist())
        old_on_players = set(self.on_players.index)
        if len(next_on_players) != 0:

            # work-around for keeping teams in on_players correct
            in_players_unordered = list(next_on_players.difference(old_on_players))
            out_players_unordered = list(old_on_players.difference(next_on_players))
            in_players_0 = list()
            in_players_1 = list()
            out_players_0 = list()
            out_players_1 = list()

            while len(in_players_unordered) > 0:
                player = in_players_unordered.pop()
                if self.all_players.at[player, 'Team_id'] == teams[0]:
                    in_players_0.append(player)
                else:
                    in_players_1.append(player)

            while len(out_players_unordered) > 0:
                player = out_players_unordered.pop()
                if self.all_players.at[player, 'Team_id'] == teams[0]:
                    out_players_0.append(player)
                else:
                    out_players_1.append(player)

            # end work-around

            in_players = in_players_0 + in_players_1
            out_players = out_players_0 + out_players_1

            for i, j in zip(out_players, in_players):
                self.substitute(i, j)
            print(f'end of period {self.period-1}')
        else:
            for i in old_on_players:
                self.substitute(i, None)
            print(f'end of game')

    def new_possession(self):
        self.poss += 1

    def score(self, team_id, score):
        self.scores[team_id] += score
        for i in self.on_players.index:
            if self.on_players.at[i,'Team_id'] == team_id:
                self.on_players.at[i, 'off_points'] = self.on_players.at[i, 'off_points'] + score
            else:
                self.on_players.at[i, 'def_points'] = self.on_players.at[i, 'def_points'] + score
        print(f'    score:\n'
              f'        {team_id} scores {score} points')

    def finish(self, output_file_name):
        file = open(output_file_name, 'wt')
        for player in self.all_players.index:
            off_points = int(self.all_players.loc[player, 'off_points'])
            def_points = int(self.all_players.loc[player, 'def_points'])
            poss = int(self.all_players.loc[player, 'poss'])
            if poss == 0:
                row = f'{self.game_id},{player},0,0'
            else:
                row = f'{self.game_id},{player},{off_points/poss},{def_points/poss}'
            file.write(f'{row}\n')
        file.close()

