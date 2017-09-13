import sc2reader

# Defining helper functions
def getEvent(name = '', replay = None):
    return list({event for event in replay.events if name in event.name})

# Handling units and unit owners
def to_dictOwner(player):
    player_dict = {}
    if player != None:
        player_dict['owner'] = player.pid
    else:
        player_dict['owner'] = -1
    return player_dict

def to_dictUnit(unit):
    wish_to_ignore = ['__','_type_class','flags','apply_flags', 'is_type', 'set_type','type_history','type']
    unit_dict = {key:unit.__getattribute__(key) for key in unit.__dir__()
            if all([ignore not in key for ignore in wish_to_ignore])}

    # Removing references to player objects
    unit_dict.update(to_dictOwner(unit_dict['owner']))
    if unit_dict['killed_by'] !=None:
        unit_dict['killed_by'] = unit_dict['killed_by'].pid
        unit_dict['killing_player'] = unit_dict['killed_by']

    # Removing references to unit objects
    unit_dict['killed_units'] = [unit.id for unit in unit_dict['killed_units']]
    if type(unit_dict['killing_unit']) != type(None):
        unit_dict['killing_unit'] = unit_dict['killing_unit'].id

    return unit_dict

# Handling events
def to_dictPlayerStatsEvent(event):
    wish_to_ignore = ['ff_','player','stats','name']
    return {key.replace('food', 'supply'):event.__dict__[key] for key in event.__dict__.keys()
            if all([ignore not in key for ignore in wish_to_ignore])}

def to_dictUnitPositionsEvent(event):
    return {'positions':{key.id:event.units[key] for key in event.units.keys()},
            'frame':event.frame,
            'second':event.second}

def to_dictUpgradeCompleteEvent(event):
    return {'upgrade_type_name':event.upgrade_type_name,
            'frame': event.frame,
            'second': event.second,
            'pid': event.pid}

def to_dictEvent(event):
    if event.name == 'PlayerStatsEvent':
        return to_dictPlayerStatsEvent(event)
    elif event.name == 'UnitPositionsEvent':
        return to_dictUnitPositionsEvent(event)
    elif event.name == 'UpgradeCompleteEvent':
        return to_dictUpgradeCompleteEvent(event)

# Helper functions
def to_dictContext(replay):
    try:
        return sc2reader.utils.toDict(replay)
    except:
        return replay.context

def to_dictObjects(replay):
    return {key:to_dictUnit(replay.objects[key]) for key in replay.objects.keys()}

def to_dictEvents(name, replay):
    events = getEvent(name, replay)
    return [to_dictEvent(event) for event in events]

# Main function 1 of 2
def to_dictReplay(replay):
    replay_dict = {}
    replay_dict['context'] = to_dictContext(replay)
    replay_dict['objects'] = to_dictObjects(replay)
    replay_dict['player_stats'] = to_dictEvents('PlayerStatsEvent', replay)
    replay_dict['unit_positions'] = to_dictEvents('UnitPositionsEvent', replay)
    replay_dict['upgrades'] = to_dictEvents('UpgradeCompleteEvent', replay)
    return replay_dict

# Helper function
def dict_to_values(key_order, dictionary):
    return [dictionary[key] for key in key_order]

# Main function 2 of 2
def to_lean_dict(dict_replay, look_up = False, deduce = False):
    object_keys = sorted(list(list(dict_replay['objects'].values())[0].keys()))
    player_stat_keys = sorted(list(dict_replay['player_stats'][0].keys()))

    if look_up == True:
        can_be_looked_up = ['is_army','is_worker','is_building','minerals','supply','title','vespene']
        object_keys = [key for key in object_keys if key not in can_be_looked_up]

    if deduce == True:
        player_stat_keys = sorted(['frame','pid',
                                   'minerals_collection_rate','minerals_current',
                                   'minerals_used_in_progress_army',
                                   'minerals_used_in_progress_economy',
                                   'minerals_used_in_progress_technology',
                                   'vespene_collection_rate','vespene_current',
                                   'vespene_used_in_progress_army',
                                   'vespene_used_in_progress_economy',
                                   'vespene_used_in_progress_technology'])

    lean_replay = dict_replay.copy()
    lean_replay['object_keys'] = object_keys
    lean_replay['player_stat_keys'] = player_stat_keys

    lean_replay['objects'] = {key: dict_to_values(object_keys, dict_replay['objects'][key])
                              for key in dict_replay['objects'].keys()}

    lean_replay['player_stats'] = [dict_to_values(player_stat_keys, event)
                                   for event in dict_replay['player_stats']]

    return lean_replay

# Wrapper function for 1 and 2
def replay_to_dict(replay, look_up = True, deduce = True):
    return to_lean_dict(to_dictReplay(replay), look_up = look_up, deduce = deduce)
