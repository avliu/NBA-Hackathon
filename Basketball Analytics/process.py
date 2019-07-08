import models


def process_game(input_dir, output_file_dir, game_id, lineups_file_name):

    game = models.Game(output_file_dir, game_id, lineups_file_name)

    file = open(f'{input_dir}/{game_id}.csv', "r")

    line_number = 0

    index = []

    for f in file:
        line_arr = f.replace("\"", "").lower().split(",")

        # grab column names
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
                time = line_dict['pc_time']
                game.substitute(person1, person2, time)

            # score
            if int(line_dict['event_msg_type']) == 1 or \
                (int(line_dict['event_msg_type']) == 3 and int(line_dict['option1']) == 1):

                team_id = line_dict['team_id']
                option1 = int(line_dict['option1'])
                pc_time = int(line_dict['pc_time'])
                game.score(team_id, option1, pc_time)

            # possession completed
            if int(line_dict['event_msg_type']) == 0:

                pc_time = int(line_dict['pc_time'])
                game.new_possession(pc_time)

        line_number += 1


game_ids_file = open('Game_ids.txt', 'r')
game_ids = game_ids_file.read().split(',')


for game_id in game_ids:
    process_game('games_marked', 'output', game_id, 'Game_Lineup.txt')
