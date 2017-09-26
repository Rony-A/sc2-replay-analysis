# Analysing StarCraft II replays

Capstone: [StarCraft II replay analysis](https://github.com/mkleinbort/sc2-replay-analysis/blob/master/Starcraft%20II%20analysis.ipynb)

I recently completed the 12-week Data Science Immersive at General Assembly, London. For my final project I 
analysed StarCraft 2 replay files and built a series of models that predict - with high accuracy - the winner of a match given the state of the game when player 1 or player 2 surrendered.

![End Game States](https://github.com/mkleinbort/sc2-replay-analysis/blob/master/Images/Capstone%20Screenshots/Screen%20Shot%202017-09-13%20at%2011.49.42.png?raw=true)

In doing this I built some interesting tools that others may find interesting, so feel free to look at the code 
and adapt it as you want.

In particular, note that I added a "get_game_state_at_t()" function in Scripts.game_state_explorer. If I have time I'll use it to build a predictive model that can anticipate the winner of a game.

Our thanks go to the developers of sc2reader; their work was absolutely essential in making this analysis possible.
Feel free to leave suggestions or feedback.

All the best,
MK.

### Key Take Aways:
##### replay_to_dict()

I was frustrated by having to spend 5-15 minutes waiting for sc2reader to parse the replay files each time I restarted my kernel. I resolved this by extracting the information I wanted (metadata, player statistics, units, upgrades, unit locations) and storing it in a json-like format that could easily be stored and loaded. After some optimisations the loading times were improved from 600ms to under 1ms per game (a 99.8% improvement). Furthermore, ram consumption was decreased by 99%.

The development of this function can be found in Appendix 1.

If you want to use it, it is as easy as:

  from Scripts.replay_to_dict import replay_to_dict
  
It expects an sc2reader.Replay object to be passed into it, and it outputs a dictionary. The structure if this dictionary is fairly intuitive, but examples of how to access the information are given in Appendix 1. and in the main notebook (Starcraft II analysis).

##### A 1-d representation of the game state

The main challenge I faced in this project was translating the game state to a 1-dimentional array, such that I could tabulate the data with each row in the table representing a game state.

Many features were readily available through data munging, but the spatial location of units and its significance was tackled using density-based clustering.

![State Representation Pipeline](https://raw.githubusercontent.com/mkleinbort/sc2-replay-analysis/master/Images/Capstone%20Screenshots/Screen%20Shot%202017-09-14%20at%2023.22.20.png)

Details can be found in the main notebook (Starcraft II analysis).

##### Some helper functions

When I started working with the .SC2Replay files the first challenge was accessing the information I wanted. To this end I developed some helper functions with some robust querying capabilities. 

In particular, the getUnits() function allows for easy querying of the replay file by unit name, type, partial name (it checks if the input is a substring of the unit's name), time of death, time of birth, owner or race. It also has a robust handling of passing multiple conditions. Details and examples can be found in Appendix 3.

I used this function to create a crude replay of games parsed by sc2reader (details in Appendix 3).


![Video moments](https://github.com/mkleinbort/sc2-replay-analysis/blob/master/Images/Capstone%20Screenshots/Screen%20Shot%202017-09-13%20at%2012.34.19.png?raw=true)

![Video using getUinits()](https://github.com/mkleinbort/sc2-replay-analysis/blob/master/Images/Video%20of%20Game%20Smooth.mov)
