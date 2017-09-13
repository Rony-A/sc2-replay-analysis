import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed
from ipywidgets import Checkbox, IntSlider

import matplotlib as mpl
import pickle

import sc2reader
from sc2reader.engine.plugins import APMTracker, SelectionTracker
sc2reader.engine.register_plugin(APMTracker())
sc2reader.engine.register_plugin(SelectionTracker())

import pandas as pd
unit_attributes_df = pd.read_pickle('./Resources/unit_attributes.p')

example_gamefile = './../../../Games/Dark_INoVation_AbyReef.SC2Replay'
replay = sc2reader.load_replay(example_gamefile)

all_event_types = {event.name for event in replay.events}

def getEvents(name = '', replay = None):
    return list({event for event in replay.events if name in event.name})

def frames_to_irl_seconds(num):
    return (num/16) / 1.4

def irl_seconds_to_frames(num):
    return num * 16 * 1.4

def getUnits(units = [], time = False,
             finished_before = np.inf, finished_after = 0,
             died_before = np.inf, died_after = 0,
             army = True, workers = True, buildings = True,
             player = None, name = None,replay = None):

    if type(time) != bool:
        died_after = time+1
        finished_before = time

    died_before = irl_seconds_to_frames(died_before)
    died_after = irl_seconds_to_frames(died_after)
    finished_before = irl_seconds_to_frames(finished_before)
    finished_after = irl_seconds_to_frames(finished_after)

    if player != None:
        units = player.units
    elif units == []:
        units = replay.players[0].units + replay.players[1].units
    else:
        units = units

    return [unit for unit in units
            if (unit.finished_at != None and
                unit.finished_at <= finished_before
                and unit.finished_at >= finished_after)

            and (unit.died_at == None
                 or unit.died_at >= died_after)

            and (died_before == np.inf or (unit.died_at != None
                 and unit.died_at <= died_before))

            and ((unit.is_army and army)
                 or (unit.is_worker and workers)
                 or (unit.is_building and buildings))

            and (name == None or name in unit.name)]

def getUnitFeatures(features = [], kwargs = {}):
    units = getUnits(**kwargs)

    attributes = [feature for feature in features if feature not in ['player_id','unit']]
    df = pd.DataFrame({feature: [unit.__getattribute__(feature) for unit in units] for feature in attributes},
                      columns=features)

    df.applymap(lambda x:np.nan if x == None else x)

    for col in list(set(df.columns) & set(['started_at','died_at', 'finished_at'])):
        df[col] = df[col].apply(frames_to_irl_seconds).apply(lambda x:int(x)
                                                             if np.isnan(x) == False
                                                             else np.complex('j'))

    special_features = [feature for feature in features if feature in ['player_id','unit']]
    if 'player_id' in special_features:
        try:
            df['player_id'] = [unit.owner.pid for unit in units]
        except:
            df['player_id'] = [unit.owner for unit in units]

    if 'unit' in special_features:
        df['unit'] = units
    return df

def mineralValue(units):
    return sum(unit.minerals for unit in units)

def gasValue(units):
    return sum(unit.vespene for unit in units)
