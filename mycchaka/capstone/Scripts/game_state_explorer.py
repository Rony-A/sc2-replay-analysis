import pandas as pd
import numpy as np

def parse_unit_data(replay_dict):
        df_units = pd.DataFrame(data = replay_dict['objects']).T
        df_units.columns = columns=replay_dict['object_keys']
        return df_units

def clean_unit_data(df_units):
    df_units['x'], df_units['y'] = zip(*df_units['location'].values)
    df_units = df_units.drop(['location'], axis=1)
    df_units['name'] = df_units['name'].apply(lambda x:x.lower())
    return df_units

def parse_stats_data(replay_dict):
    df_stats = pd.DataFrame(data = replay_dict['player_stats'])
    df_stats.columns = columns=replay_dict['player_stat_keys']
    return df_stats

def parse_upgrade_data(replay_dict):
    df_upgrades = pd.DataFrame(replay_dict['upgrades'])
    return df_upgrades

def clean_upgrade_data(df_upgrades):
    return df_upgrades[['SprayTerran' not in x and 'Reward'
        not in x for x in df_upgrades['upgrade_type_name']]]

def parse_outcome_data(replay_dict):
    outcome = {player['result']:player['pid'] for player in replay_dict['context']['players']}
    return outcome

def preliminary_processing(replay_dict):
    dict_of_dataframes = {'units': clean_unit_data(parse_unit_data(replay_dict)),
                          'stats': parse_stats_data(replay_dict),
                          'upgrades': clean_upgrade_data(parse_upgrade_data(replay_dict)),
                          'context': replay_dict['context'],
                          'outcome':parse_outcome_data(replay_dict)}
    return dict_of_dataframes

def get_stats_at_t(dict_of_dataframes, t = np.inf):
        df = dict_of_dataframes['stats'].sort_values(by='frame')

        p1 = df[df['pid']==1]
        p1 = p1[p1['frame'] <= t].tail(1).to_dict()

        p2 = df[df['pid']==2]
        p2 = p2[p2['frame'] <= t].tail(1).to_dict()

        # We use the prefix S to specify that a specific feature is stats data.
        p1 = {'1'+'S_'+key:list(p1[key].values())[0] for key in p1.keys()}
        p2 = {'2'+'S_'+key:list(p2[key].values())[0] for key in p2.keys()}

        return pd.Series({**p1,**p2}).drop(['1S_frame','2S_frame','1S_pid','2S_pid'])

def get_upgrades_at_t_part_1(dict_of_dataframes, t = np.inf):
    if dict_of_dataframes['upgrades'].shape[0] == 0:
        upgrades = None
    else:
        df = dict_of_dataframes['upgrades']
        df = df[df['frame'] <= t]
        upgrades = df.drop(['frame','second'], axis=1)\
            .groupby('pid')\
            .apply(lambda x: pd.get_dummies(x, prefix=[str(x['pid'].iloc[0])+'U']))\
            .drop(['pid'], axis=1)\
            .sum()

    return upgrades

def get_upgrades_at_t_part_2(upgrades):
    variable = None
    if not upgrades is None:
        upgrades = [name[:-1] if name[-1].isdigit() else name for name in upgrades.index]
        variable = pd.Series(upgrades).value_counts()

    return variable

def get_upgrades_at_t(dict_of_dataframes, t = np.inf):
    return get_upgrades_at_t_part_2(get_upgrades_at_t_part_1(dict_of_dataframes,t))

def get_unit_tally_at_t(dict_of_dataframes, t = np.inf):
        """returns a series with tallies of units
        for each player at the end of the game"""
        df = dict_of_dataframes['units']
        df['died_at'] = df['died_at'].apply(lambda x:np.inf if x is None else x)

        # We select the units that never died, belonnging to either player
        df = df[df['died_at'] >= t+1]
        df = df[df['finished_at'] < t]
        df = df[df['race']!= 'Neutral']

        # We prefix the unit names with the player id, and unit race initial (T,Z or P)
        tally = df[['owner','race','name']]\
                 .apply(lambda x: str(x['owner'])+x['race'][0]+'_'+ x['name'], axis=1)\
                 .value_counts()
        return tally

def preserve_context(dict_of_dataframes):
    info_part1 = {key:dict_of_dataframes['context'][key]
              for key in ['date','release','filename','frames','map_name','time_zone']}

    info_part2 = [{'{}_'.format(i+1)+key:dict_of_dataframes['context']['players'][i][key]
                  for key in ['name', 'play_race','handicap']} for i in [0,1]]

    return pd.Series({**info_part1, **{**info_part2[0],**info_part2[1]}})

def get_game_state_at_t(game, t):
    if len(game['context']['players']) != 2:
        return None

    game = preliminary_processing(game)

    stats_features = get_stats_at_t(game,t)
    upgrade_features = get_upgrades_at_t(game,t)
    unit_tally_features = get_unit_tally_at_t(game, t)
    context_data = preserve_context(game)
    outcome = pd.Series(game['outcome'])

    return pd.concat([stats_features, upgrade_features, unit_tally_features,context_data,outcome])
