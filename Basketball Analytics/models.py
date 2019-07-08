import pandas as pd


class Game:
    def __init__(self, output_dir, game_id, lineups_file):

        lineups = pd.read_csv(filepath_or_buffer=lineups_file, sep='\t')
        all_players = lineups.loc[(lineups['Game_id'] == game_id) & (lineups['Period'] == 0)][['Person_id', 'Team_id']]
        all_players = all_players.set_index('Person_id')
        for stat in ['off_points', 'def_points', 'poss']:
            all_players[stat] = [0 for i in range(len(all_players))]

        on_players = lineups.loc[(lineups['Game_id'] == game_id) & (lineups['Period'] == 1)][['Person_id', 'Team_id']]
        on_players = on_players.set_index('Person_id')

        teams = all_players['Team_id'].unique()
        self.all_players = all_players
        self.on_players = on_players
        self.lineups = lineups
        self.teams = teams
        self.scores = dict(zip(teams, [0, 0]))
        self.poss = 0
        self.period = 1
        self.game_id = game_id
        self.output_dir = output_dir

        self.queue = pd.DataFrame(columns=['leaving', 'entering', 'sub_time'])
        print(f'processing game {game_id}')

    def substitute(self, leaving_player, entering_player, sub_time):

        self.queue = self.queue.append({'leaving':leaving_player, 'entering':entering_player, 'sub_time':sub_time},
                                       ignore_index=True)

    def new_possession(self, poss_end_time):
        self.poss += 1

        poss_players = set(self.on_players.index)
        for i in range(0, self.queue.shape[0]):
            if int(self.queue.loc[i, 'sub_time']) > poss_end_time:
                poss_players.add(self.queue.loc[i, 'entering'])

        for poss_player in poss_players:
            self.all_players.loc[poss_player, 'poss'] += 1

        for i in range(0, self.queue.shape[0]):
            leaving_player= self.queue.loc[i, 'leaving']
            entering_player = self.queue.loc[i, 'entering']

            if entering_player:
                as_list = self.on_players.index.tolist()
                idx = as_list.index(leaving_player)
                as_list[idx] = entering_player
                self.on_players.index = as_list

        self.queue = pd.DataFrame(columns=['leaving', 'entering', 'sub_time'])

    def score(self, team_id, score, score_time):
        self.scores[team_id] += score

        scoring_players = set(self.on_players.index)
        for i in range(0, self.queue.shape[0]):
            if int(self.queue.loc[i, 'sub_time']) > score_time:
                scoring_players.remove(self.queue.loc[i, 'leaving'])
                scoring_players.add(self.queue.loc[i, 'entering'])

        for scoring_player in scoring_players:
            if self.all_players.at[scoring_player, 'Team_id'] == team_id:
                self.all_players.at[scoring_player, 'off_points'] += score
            else:
                self.all_players.at[scoring_player, 'def_points'] += score

    def new_period(self):
        self.period += 1

        next_on_players = set(self.lineups.loc[(self.lineups['Game_id'] == self.game_id) &
                                          (self.lineups['Period'] == self.period)]['Person_id'].values.tolist())
        old_on_players = set(self.on_players.index)
        for i in range(0, self.queue.shape[0]):
            old_on_players.remove(self.queue.loc[i, 'leaving'])
            old_on_players.add(self.queue.loc[i, 'entering'])

        if len(next_on_players) > 0:

            # work-around for keeping teams in on_players correct
            in_players_unordered = list(next_on_players.difference(old_on_players))
            out_players_unordered = list(old_on_players.difference(next_on_players))
            in_players_0 = list()
            in_players_1 = list()
            out_players_0 = list()
            out_players_1 = list()

            while len(in_players_unordered) > 0:
                player = in_players_unordered.pop()
                if self.all_players.at[player, 'Team_id'] == self.teams[0]:
                    in_players_0.append(player)
                else:
                    in_players_1.append(player)

            while len(out_players_unordered) > 0:
                player = out_players_unordered.pop()
                if self.all_players.at[player, 'Team_id'] == self.teams[0]:
                    out_players_0.append(player)
                else:
                    out_players_1.append(player)

            # end work-around

            in_players = in_players_0 + in_players_1
            out_players = out_players_0 + out_players_1

            for i, j in zip(out_players, in_players):
                self.queue = self.queue.append({'leaving': i, 'entering': j, 'sub_time': 0}, ignore_index=True)

        else:
            for i in old_on_players:
                self.queue = self.queue.append({'leaving': i, 'entering': None, 'sub_time': 0}, ignore_index=True)
            self.new_possession(0)
            self.finish()

    def finish(self):
        file = open(f'{self.output_dir}/{self.game_id}.csv', 'wt')
        file.write('Game_ID,Player_ID,OffRtg,DefRtg\n')
        for player in self.all_players.index:
            off_points = int(self.all_players.loc[player, 'off_points'])
            def_points = int(self.all_players.loc[player, 'def_points'])
            poss = int(self.all_players.loc[player, 'poss'])
            if poss == 0:
                row = f'{self.game_id},{player},0,0'
            else:
                row = f'{self.game_id},{player},{off_points / poss * 100},{def_points / poss * 100}'
            file.write(f'{row}\n')
        file.close()