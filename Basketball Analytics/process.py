import pandas as pd
import models
import os


def process_game(game_id, lineups_file_name, output_file_name):
    lineups = pd.read_csv(filepath_or_buffer=lineups_file_name, sep='\t')

    game = models.Game(game_id, lineups)

    file = open(f'games/{game_id}.csv', "r")

    line_number = 0

    index = []

    for f in file:
        line_arr = f.replace("\"", "").lower().split(",")

        if line_number == 0:
            index = line_arr

        else:
            line_dict = dict(zip(index, line_arr))

            # period change
            if int(line_dict['event_msg_type']) == 13:
                game.new_period()

            # substitution
            if int(line_dict['event_msg_type']) == 8:
                person1 = line_dict['person1']
                person2 = line_dict['person2']
                game.substitute(person1, person2)

            # score
            if int(line_dict['event_msg_type']) == 1 or \
                (int(line_dict['event_msg_type']) == 3 and int(line_dict['option1']) == 1):
                game.score(line_dict['team_id'], int(line_dict['option1']))

            # possession completed

        line_number += 1

    game.finish(output_file_name)


game_ids_file = open('Game_ids.txt', 'r')
game_ids = game_ids_file.read().split(',')

for game_id in game_ids:
    process_game(game_id, 'Game_Lineup.txt', 'Output.txt')
