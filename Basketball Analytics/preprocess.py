import pandas as pd
import csv


def assign_teams(file_name, out_file_name):
    plays_original = open(file_name, 'r')
    plays_updated = open(out_file_name, 'wt')
    writer = csv.writer(plays_updated)
    lineups = pd.read_csv(filepath_or_buffer='Game_Lineup.txt', sep='\t')

    skip = 0
    for play in plays_original:
        play_arr = play.strip().replace("\"", "").lower().split("\t")
        if skip == 0:
            pass
        else:
            try:
                play_arr[10] = lineups.loc[(lineups['Game_id'] == str(play_arr[0])) &
                                           (lineups['Period'] == 0) &
                                           (lineups['Person_id'] == str(play_arr[11]))]['Team_id'].values[0]
            except:
                print('could not find team for line ', skip, ', event is ', play_arr[2], ', ', play_arr[6])

        writer.writerow(play_arr)

        skip += 1


def mark_possessions(file_name, out_file_name):
    plays_original = open(file_name, 'r')
    plays_updated = open(out_file_name, 'wt')

    line_number = 0
    index = []

    free_throw_team = ''
    poss_flag_1 = False
    poss_flag_2 = False
    poss_end_time = -1
    poss_end_str_1 = '0,0,0,0,0,'
    poss_end_str_2 = ',0,0,0,0,0,0,0,0,0,0,0,0\n'

    for play in plays_original:
        line_arr = play.split(",")

        # write column names
        if line_number == 0:
            index = line_arr
            plays_updated.write(f'{play}')

        else:
            play_dict = dict(zip(index, line_arr))
            event_msg_type = int(play_dict['event_msg_type'])
            action_type = int(play_dict['action_type'])
            option_1 = int(play_dict['option1'])
            pc_time = int(play_dict['pc_time'])
            team_id = play_dict['team_id']

            # wait for time to change
            if poss_flag_1 and poss_flag_2:
                if pc_time != poss_end_time:
                    plays_updated.write(f'{poss_end_str_1}{poss_end_time}{poss_end_str_2}')
                    poss_flag_1 = False
                    poss_flag_2 = False

            # made basket or made final free throw (excluding flagrants free throws)
            if (event_msg_type == 1) or \
                    (event_msg_type == 3 and action_type == 10 and option_1 == 1) or \
                    (event_msg_type == 3 and action_type == 12 and option_1 == 1) or \
                    (event_msg_type == 3 and action_type == 15 and option_1 == 1) or \
                    (event_msg_type == 3 and action_type == 16 and option_1 == 1) or \
                    (event_msg_type == 3 and action_type == 17 and option_1 == 1) or \
                    (event_msg_type == 3 and action_type == 22 and option_1 == 1) or \
                    (event_msg_type == 3 and action_type == 26 and option_1 == 1) or \
                    (event_msg_type == 5) or \
                    (event_msg_type == 13):
                poss_flag_1 = True
                poss_flag_2 = True
                poss_end_time = pc_time

            # missed shot or final free throw, still need a defensive rebound
            elif (event_msg_type == 2) or \
                    (event_msg_type == 3 and action_type == 10 and option_1 == 0) or \
                    (event_msg_type == 3 and action_type == 12 and option_1 == 0) or \
                    (event_msg_type == 3 and action_type == 15 and option_1 == 0) or \
                    (event_msg_type == 3 and action_type == 16 and option_1 == 0) or \
                    (event_msg_type == 3 and action_type == 17 and option_1 == 0) or \
                    (event_msg_type == 3 and action_type == 22 and option_1 == 0) or \
                    (event_msg_type == 3 and action_type == 26 and option_1 == 0):
                poss_flag_1 = True
                free_throw_team = team_id

            # defensive rebound after a missed shot or final free throw
            elif poss_flag_1 and event_msg_type == 4 and team_id != free_throw_team:
                poss_flag_2 = True
                poss_end_time = pc_time

            plays_updated.write(f'{play}')

        line_number += 1
    plays_updated.write(f'{poss_end_str_1}50000{poss_end_str_2}')


def split_games(in_file_name, out_folder_name):
    in_file = open(in_file_name, 'r')
    games = ''
    game = ''
    index = None
    out_file = None
    skip = 0
    for play in in_file:
        play_arr = play.strip().replace("\"", "").lower().split(",")
        if skip == 0:
            index = play
            pass
        else:
            if play_arr[0] != game:
                game = play_arr[0]
                if out_file:
                    out_file.close()
                out_file = open(f'{out_folder_name}/{game}.csv', 'wt')
                games += game + ','
                out_file.write(f'{index}')
            out_file.write(f'{play}')
        skip += 1

    games = games[0:-1]
    games_file = open('Game_ids.txt', 'wt')
    games_file.write(games)
    games_file.close()


# 1.
# assign_teams('Play_by_Play.txt', 'Play_by_Play_Processed.csv')

# 2.
# IN EXCEL:
# Load data, delete blank rows
# Sort by required time columns
# CSV now saved in 'Play_by_Play_Processed_Time.csv'

# 3.
# split_games('Play_by_Play_Processed_Time.csv', 'games')

# 4.
# game_ids_file = open('Game_ids.txt', 'r')
# game_ids = game_ids_file.read().split(',')
# for game_id in game_ids:
#     mark_possessions(f'games/{game_id}.csv', f'games_marked/{game_id}.csv')
