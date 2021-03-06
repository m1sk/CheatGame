GAME RULES
==========
two players initially receive 8 cards from a standard 52 card deck
one additional card is placed, face up, on the table
the goal is to be the first player that gets rid of all her cards
at each turn the players have the following possible moves:
- take a card from the deck
- make a claim:
  place 1-4 cards of an adjacent rank to previous claim. e.g if previous rank was King, place either 1-4 Queens or Aces.
  The claim is made publicly, but the actual cards are placed face down,
  and the cards do not have to match the claim - i.e. false claim
- call "cheat":
  if the player suspects that the previous claim was false she can "call cheat".
  The last claim is examined:
  if truthful => caller takes all cards from the claim pile on table
  if false => claimer (previous player) takes all cards from the table
  the game continues from the last claim (even if it was false)

Files
=====
cheat_game_server.py - game server and utility functions. should be imported and not edited
cheat_game_client.py - a simplistic demo agent, should be used as a scaffold for intelligent agent development

Development environment
=======================
Use Python 2.7.x
recommended IDE - PyCharm by JetBrains
The IDE enables convenient editing/refactorig/debugging/running
Ctrl-Q can be used to access function description of server classes and functions

Guidelines
==========
register by sending an email with your both your names and email addresses to h.rosemarin@gmail.com
you will receive a project id shortly
create a new file: cheat_game_client_XX.py
where XX is your project id
create a class "Agent_XX(Agent)" - derived from class Agent
place your agent's logic in the function "agent_logic". look at the DemoAgent's interface.
try and make the agent play as good as possible (hopefully it should beat you at least in some of the games)
your agent will run a few times against ALL other agents.
word of caution - do not attempt to access private data (e.g. opponent cards etc)

Support
=======
you are encouraged to use the online forum:
https://groups.google.com/forum/#!forum/adv-ai-cheat-game
optionally contact: h.rosemarin@gmail.com , email Subject: "Advanced AI - Cheat Game Agent"
