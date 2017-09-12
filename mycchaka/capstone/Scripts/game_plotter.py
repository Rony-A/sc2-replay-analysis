# Imports and configurations
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed
from ipywidgets import Checkbox, IntSlider

import matplotlib as mpl
import pickle

from Scripts.mklib import plist

import sc2reader
from sc2reader.engine.plugins import APMTracker, SelectionTracker
sc2reader.engine.register_plugin(APMTracker())
sc2reader.engine.register_plugin(SelectionTracker())

# ===

# Setting plotting options
sns.set_palette([
 (0.30, 0.45, 0.69),
 (0.33, 0.66, 0.41),
 (0.77, 0.31, 0.32),
 (0.80, 0.73, 0.45),
 (0.39, 0.71, 0.80)])

import matplotlib.pylab as pylab
params = {'legend.fontsize': 14,
         'axes.labelsize': 14,
         'axes.titlesize':20}
pylab.rcParams.update(params)


plt.style.use('seaborn-white')

# ===

unit_attributes_df = pd.read_pickle('./Resources/unit_attributes.p')

def plot_unit_properties():
    df = unit_attributes_df.sort_values(by = ['Vespene','Mineral'], ascending = False)
    df[['Life','Shields']] = df[['Life','Shields']].applymap(lambda x: -x)
    fig, axes = plt.subplots(nrows=1, ncols=3)

    races = ['Terran','Zerg','Protoss']
    for i,race in enumerate(races):
        df[df['Race'] == race][
            ['Unit','Mineral','Vespene','Life','Shields']
        ].plot(x = 'Unit',kind='barh',figsize=(20, 8),
               fontsize = 14,
               stacked= True, ax = axes[i])
        axes[i].set_ylabel('')
        axes[i].set_title(race + ' Units',size= 20)
    plt.tight_layout(w_pad=1)
    plt.show()

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

def plot_information_computed_from_unit_tallies():
    units_df_over_time = pd.Series(
        {t:getUnitFeatures(['supply','is_army','is_worker','minerals','vespene','player_id'],kwargs={'replay':replay, 'time':t}
                                ) for t in range(0,int(frames_to_irl_seconds(replay.frames)),4)})

    army_supply = units_df_over_time.apply(lambda x:x[x['is_army'] == True].groupby('player_id')['supply'].sum())
    worker_supply = units_df_over_time.apply(lambda x:x[x['is_worker'] == True].groupby('player_id')['supply'].sum())

    mineral_value = units_df_over_time.apply(lambda x:x.groupby('player_id')['minerals'].sum())
    vespene_value = units_df_over_time.apply(lambda x:x.groupby('player_id')['vespene'].sum())

    fig, axes = plt.subplots(nrows=2, ncols=2)

    army_supply.plot(ax=axes[0,0], figsize=(20,6), title='Army supply')
    army_supply.plot(ax=axes[0,1], figsize=(20,6), title='Worker population')
    mineral_value.plot(ax=axes[1,0], figsize=(20,6), title = 'Total mineral value of units')
    vespene_value.plot(ax=axes[1,1], figsize=(20,6), title = 'Total vespene value of units')

    plt.subplots_adjust(hspace = 0.5)
    plt.suptitle('Some game metrics over time\n(Player 1 wins)', size=20, y=1.05)
    plt.show()

def getXY(iterable):
    return [[obj[0] for obj in iterable],[obj[1] for obj in iterable]]

def getLocations(units):
    return [unit.location for unit in units]

def getUnitType(units = [], name = ''):
    return [unit for unit in units if name in unit.name]

def plotGameState(replay = None,
                 time = 0,
                 minerals = True,
                 vespene = True,
                 towers = True,
                 workers = True,
                 army = True,
                 buildings = True,
                 ramps = True,
                 kwargs = {}):

    kwargs['time'] = time

    all_units = list(replay.active_units.values())
    p1 = replay.players[0]
    p2 = replay.players[1]

    terran_colors = ['#0703d4','#e31a00']
    zerg_colors   = ['#a01cd9','#e00283']
    protos_colors = ['e6cf00', '#e89b00']

    classic_colors = {'Terran':terran_colors,
                      'Zerg':zerg_colors,
                      'Protoss':protos_colors}

    p1c = classic_colors[replay.players[0].play_race][0]
    p2c = classic_colors[replay.players[1].play_race][1]


    if minerals:
        mineralfields = getXY(getLocations(getUnitType(all_units, name = 'MineralField')))
        plt.scatter(mineralfields[0], mineralfields[1], color = '#44a7f2', alpha=1)

    if vespene:
        vespenegeyser = getXY(getLocations(getUnitType(all_units, name = 'VespeneGeyser')))
        plt.scatter(vespenegeyser[0], vespenegeyser[1], color = '#3ed121', alpha=1)

    if towers:
        xelnagatowers = getXY(getLocations(getUnitType(all_units, name = 'XelNagaTower')))
        plt.scatter(xelnagatowers[0], xelnagatowers[1], color = 'k', alpha=0.5)

    if ramps:
        destructibleramp = getXY(getLocations(getUnitType(all_units, name = 'Destructible')))
        plt.scatter(destructibleramp[0], destructibleramp[1], color = 'orange', alpha=0.5, s = 100, marker='s')

    if workers:
        p1workers = getXY(getLocations(getUnits(player=p1,workers=True, army = False, buildings = False, **kwargs)))
        p2workers = getXY(getLocations(getUnits(player=p2,workers=True, army = False, buildings = False, **kwargs)))

        plt.scatter(p1workers[0], p1workers[1], color = p1c, s = 10)
        plt.scatter(p2workers[0], p2workers[1], color = p2c, s = 10)

    if army:
        p1army = getXY(getLocations(getUnits(player=p1,workers=False, army = True, buildings = False, **kwargs)))
        p2army = getXY(getLocations(getUnits(player=p2,workers=False, army = True, buildings = False, **kwargs)))

        plt.scatter(p1army[0], p1army[1], color = p1c, s = 10, marker='*', alpha=0.5)
        plt.scatter(p2army[0], p2army[1], color = p2c, s = 10, marker='*', alpha=0.5)

    if buildings:
        p1buildings = getXY(getLocations(getUnits(player=p1,workers=False, army = False, buildings = True, **kwargs)))
        p2buildings = getXY(getLocations(getUnits(player=p2,workers=False, army = False, buildings = True, **kwargs)))

        plt.scatter(p1buildings[0], p1buildings[1], c = p1c, s = 100, marker='s', alpha=0.5)
        plt.scatter(p2buildings[0], p2buildings[1], c = p2c, s = 100, marker='s', alpha=0.5)

    minx = min(mineralfields[0]) - 20
    maxx = max(mineralfields[0]) + 20
    miny = min(mineralfields[1]) - 20
    maxy = max(mineralfields[1]) + 20
    plt.xlim([minx,maxx])
    plt.ylim([miny,maxy])

#plt.title('Map: ' + current_game.map_name + '\n'
#          + 'Players: ' + current_game.players[0].name + ' / ' + current_game.players[1].name)
    plt.show()

def plwrap(time = 0, **kwargs):
    plotGameState(time=time, replay=current_game, **kwargs)
    return None

def plot_replay_of_current_game():
    current_game = replay
    interact(plwrap, time=IntSlider(min=0, max=frames_to_irl_seconds(replay.frames), step=4))
    return None
