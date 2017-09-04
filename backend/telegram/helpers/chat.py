

def help_text():
    return """List of commands to participate in game.
    
/games - list of games
/game_participate <index> - take part in one of games
"""

def help_description_text():
    return """
Hi I am simple lottery bot.

My purpose is to provide simple and open lottery where you can participate and win if you are luck enough.

Once you have run command /start I remember you.

What you should know about me:

- I accept ethereum (cryptocurrency) and at current time this is only available currency
- Games are based on smart contracts that guaranties that no one has an advantage. Everything is fair.

If this terms confuses or/and you have no clue on them I would suggest to look through this site:
https://www.ethereum.org/
 
How does it work?

Simple.

You choose game to participate. Right now we have 1, 5, 10 and 30 minutes lotteries.
 
Every 1, 5, 10 and 30 minutes system chooses winner out of participants.

Every game has corresponding price. You should see actual price for each game in menu or description.

Let's take example of 5 minute lottery.

During 5 minutes (for instance since 12:00 - 12:05) players pay price to participate.

Lets for example take 0.1 ether.

There are 10 players (including you), and overall 1 ether.

When clock hits 12:05:00 game ends and random player is choosen as a winner. Your chance of winning is 1/10.

The longer the game, more players will probably participate and higher prize will be but lower your chances. In general
higher prize - higher risk.

If there was only 1 player, game keeps going.

One important point.

Total prize is shared. You get half of the prize, another half goes to selected charity.

That's where ether helps us. Blockchain technology allows not just provide fair and transparent randomization but 
to report the flow of money. You can actually see how much was provided to charity and see that money was going the\
right way.
 
We also take a little. To run lottery we run servers and pay our supprot team.
 
We are open and hope we were able to gain your trust.

How can I play?

%s
""" % (help_text())