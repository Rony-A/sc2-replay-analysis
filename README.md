# Analyzing StarCraft II replays

I just finished the 12-week Data Science Immersive at General Assembly, London. For my final project I 
analized StarCraft 2 replay files and built a series of models that can - with high accuracy - determine 
the winner of a match given the state of the game when player 1 or player 2 surrendered.

In doing this I think I built some interesting tools that others may find interesting, so feel free to look at the code 
and adapt it as you want.

In particular note that we added a "get_game_state_at_t()" function in Scripts.game_state_explorer. If I have time I'll use it to
build a predictive model that can antisipate the winner of a game.

Our thanks go to the developers of sc2reader, their work was absolely essential in making this analysis possible.
Feel free to leave sugestions or feedback.

All the best,
MK.
