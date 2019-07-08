import pandas as pd


game_ids_file = open('Game_ids.txt', 'r')
game_ids = game_ids_file.read().split(',')

df = pd.DataFrame(columns=('Game_ID', 'Player_ID', 'OffRtg', 'DefRtg'))
for game_id in game_ids:
    df = df.append(pd.read_csv(f'output/{game_id}.csv'), ignore_index=True)

df.to_csv('Alex_Liu_Q1_BBALL.csv', index=False)
