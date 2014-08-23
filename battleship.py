######################################################
#
#        	Battleship Game
#   		started 8/3/14
#			working version completed 8/13/14
#
#
######################################################

import math
import random
import sys

########  Constants             ##############################

Ship = {'A' : ["Aircraft Carrier", 5], 'B' : ["Battleship", 4], 'D' : ["Destroyer", 3], 'S' : ["Submarine", 3], 'P' : ["Patrol Boat", 2]}
HIT= "  X  "
MISS = "  O  "
HIDDEN = " --- "

########   Class Definitions  ##############################

class Player:
	"""
	Each player is given a name and potentially will have scores and
	battle points. Each player will be given a board and 5 ships to 
	place on the board. 
	"""
	def __init__(self, name = "Anonymous"):
		"""
		Initialize player with name, score, and battle points.
		"""
		self._name = name
		self._score = 0
		self._battle_points = 0
		
	def __str__(self):
		"""
		Returns the name of the player.
		"""
		return self._name		 

class Board:
	"""
	Class representation of playing board. Each player will have their
	own board.
	"""
	def __init__(self, player = Player(), size = 10):
		self._player = str(player)
		self._size = size
		self._grid = set([(row,col) for row in range(self._size)
									for col in range(self._size)])
		self._status = [[HIDDEN for col in range(self._size)]
										for row in range(self._size)]							
		self._unused = set(self._grid)
		self._used = set()
		self._hidden = set(self._grid)
		
	def __str__(self):
		"""
		Generates a string representation for the board
		returns a string
		"""
		print self._player + "'s board:"
		board = "    "
		for col in range(self._size):
			board += "  " + str(col) + "  "  
		board += "\n   +" + "-----" * 10 + "+\n"
		for row in range(self._size):
			board += str(row) + "  |"
			for col in range(self._size):
				board += self._status[row][col]
			board += "|\n"
		board += "   +" + "-----" * 10 + "+\n\n"
		return board
		
	def get_grid(self):
		"""
		Returns a set of tuples referencing the squares on the board.
		"""
		return self._grid
		
	def get_size(self):
		"""
		Returns the length of the board (all boards are square)
		"""
		return self._size
		
	def get_player(self):
		"""
		Returns the string representation of the owner of the board.
		"""
		return self._player
		
	def update_used(self, new = ()):
		"""
		Adds new to set of used squares
		"""
		self._used.update(set(new))

		
	def update_unused(self, new = ()):
		"""
		Adds new to set of unused squares
		"""
		self._unused.update(set(new))
		# print self._unused
		
	def remove_used(self, new = ()):
		"""
		Removes new from set of used squares
		"""
		self._used.difference_update(set(new))
		
	def remove_unused(self, new = ()):
		"""
		Removes new from set of unused squares
		"""
		self._unused.difference_update(set(new))
		
	def get_unused(self):
		"""
		Returns unused squares
		"""
		return self._unused
		
	def get_used(self):
		"""
		Returns used squares
		"""
		return self._used

		
	def update_status(self, pos = None, new_status = HIDDEN):
		"""
		Updates the entry in self._status at grid position pos to reflect the hits
		received during the game. 
		"""
		if pos != None:
			self._status[pos[0]][pos[1]] = new_status
		return None
		
	def get_status(self, pos = None):
		"""
		Returns the visible status of the position on the board.
		"""
		return self._status[pos[0]][pos[1]]
		
	def check_available(self, pos_set):
		return set(pos_set) <= set(self._unused)
		
class Naval_Vessel:
	"""
	Naval_Vessel class will give methods common to all ships in the game. Owner, length, type of vessel, status (hidden, hit, sunk)
	and current location will adjusted using these methods. Each ship is tied to a specific board.
	"""
	def __init__(self, board = Board(), code = "A", berth = None, orientation = 0):
		"""
		Initialize the Naval Vessel Class to have berth location, horizontal orientation, and status hidden
		"""
		self._board = board
		self._player = board.get_player()
		self._code = code
		self._name = Ship[code][0]
		self._length = Ship[code][1]
		self._location = berth   # position of the ship's helm as a tuple
		self._orientation = orientation    # 0 is horizontal, 1 is vertical
		self._hits = set()
		self._sunk = False
		
	def __str__(self):
		"""
		Returns string indicating player, their ship, its location, and its status in symbols
		"""
		return self._player +  "'s " + self._name + ", Location = " + str(self.get_location())
		
	def get_helm(self):
		"""
		Returns helm location as an ordered pair
		"""
		return self._location
	
	def get_location(self):
		"""
		Returns a list of tuples on board occupied by the ship. If the ship is still at the berth it
		returns None.
		"""
		if self._location == None:
			return None
		hpos = self._location          # this is just the position of the helm
		ori = self._orientation
		return [(hpos[0] + ori*idx  , hpos[1] +  ((ori + 1)%2 )*idx) for idx in range(self._length)]
		
	def get_code(self):
		"""
		Returns code for printing when ship is sunk.
		"""
		return "  " + self._code + "  "
		
	def change_orientation(self):
		"""
		flips the ship's orientation
		"""
		self._orientation = (self._orientation + 1 ) % 2
		return
		
	def set_orientation(self,orientation):
		"""
		Allows user to set the actual orientation.
		"""
		if orientation in [0,1]:
			self._orientation = orientation
		return
		
	def get_length(self):
		"""
		Returns the length of the ship
		"""
		return self._length
		
	def move(self, pos, ori = None):
		"""
		Changes the ship's location so that its helm is at pos. The full location is then determined
		by its length and orientation. The helm is always positioned at the top or far left of the vessel
		If the new position is unavailable, the ship will not be moved.
		Return True if a move was successful
		"""
		if ori == None:
			ori = self.get_orientation()
		if self._location != None:
			self._board.remove_used(self.get_location())       # this lifts the ship off the board
			self._board.update_unused(self.get_location())    # and makes those squares available again
		
		#  now check if the new position is available. If so, reset the helm to this position
		new_pos = [(pos[0] + ori*idx  , pos[1] +  ((ori + 1)%2 )*idx) for idx in range(self._length)]
		if self._board.check_available(set(new_pos)):
			self._location = pos
			self._orientation = ori
			self._board.update_used(set(new_pos))
			self._board.remove_unused(set(new_pos))
			return True
		else:
			print "Requested location not available, try another spot or shift the orientation."
			if self.get_location() != None:
				self._board.update_used(self.get_location()) # this puts the ship back where it was
				self._board.remove_unused(self.get_location())
			return False
		


	def check_damages(self, pos):
		"""
		Determines if the ship is on a certain square on the board. Returns boolean.
		"""
		return pos in set(self.get_location())
		
	def update_status(self, pos):
		"""
		Given a grid position tuple, the position will be added to the hits and the total
		number of hits will be returned
		"""
		if pos in set(self.get_location()):
			self._hits.add(pos)
			if len(self._hits) == self._length:
				for hit in list(self._hits):
					self._board.update_status(hit, self.get_code())
				print "You sank my " + self._name + "!"
				self._sunk = True
			else:
				self._board.update_status(pos, HIT)
		return len(self._hits)

class Fleet:
	"""
	Each player is given 5 ships (Naval Vessels) to play with. At the beginning of 
	the game the ships are located in a berth. During the set up stage each player
	will move their ships to a place on their board.  This class will keep track of the
	position of the fleet and the health (the number of hits) of each vessel.	 When all
	vessels are sunk the player concedes the game.
	"""
	def __init__(self, board = Board(), manual = True, berth = None):
		"""
		The type of Fleet will depend on whether the player is manually controlling the 
		boats or the computer is controlling the boats. I the latter case the Fleet will
		be initialized on the board in random locations. If manual = True then additional
		functions must be called to place the ships.
		"""
		self._board = board
		self._player = str(board.get_player())
		self._manual = manual
		self._health = 17
		if manual == True:
			self._fleet = {}
			for vessel in Ship.iterkeys():
				self._fleet[vessel] = Naval_Vessel(board, vessel)
				
			# print self._fleet


		else:
			self._fleet = {}
			for vessel in Ship.iterkeys():
				berth, orientation = create_ship(self._board, vessel)
				self._fleet[vessel] = Naval_Vessel(self._board, vessel, berth, orientation)
				
		self._berth = berth
		
	def __str__(self):
		"""
		Returns a list of Vessels
		"""
		fleet = str(self._board.get_player()) + "'s Fleet:\n"
		for vessel in self._fleet.itervalues():
			fleet += "  " + str(ship) + "\n"
		return str(fleet)
		
	def get_health(self):
		"""
		How many spots in the Fleet are still hidden?
		"""
		return self._health
		
	def check_for_damages(self, pos_set):
		"""
		Checks if a pos is on one of the ships in the fleet. If it is it updates the status
		of the ships and the board.
		"""

		for pos in pos_set:
			hit = False
			for ship in self._fleet.itervalues():
				if pos in ship.get_location():
					print str(pos) + " is a HIT"
					hit = True
					ship.update_status(pos)
					self._health -= 1
					if self._health == 0:
						print self._player + "'s fleet is Destroyed. Game Over."
						print self._board
						sys.exit(0)				
			if hit == False:
				print str(pos) + " is a MISS"
				self._board.update_status(pos,MISS)
			print self._board
		return 
		
	def get_fleet_list(self):
		"""
		Returns a list of all positions held by fleet along with the corresponding codes
		List has the form [ [pos,code] ...]
		"""
		fleet = set()
		for ship in self._fleet.itervalues():
			for pos in ship.get_location():
			 	fleet.update([pos, ship.get_code()])
		return fleet
		
	def get_fleet(self):
		"""
		Returns the self._fleet dictionary to reference individual ships in the fleet.
		"""
		return self._fleet
		
	def get_player(self):
		"""
		Returns the player for this fleet
		"""
		return self._board.get_player()
	
class Strategy:
	"""
	Class representation of automated strategy for search and strike
	of ships on Battleship Game board.
	"""
	def __init__(self, board = Board(), fleet = Fleet()):
		"""
		Initialize the strategy with a blank board. Only even numbered
		squares will be struck at random.
		"""
		self._board = board
		self._fleet = fleet
		self._grid = [ (x,y) for x in range(0,10) for y in range(0,10)]
		self._checkers = [pos for pos in self._grid if (pos[1] + pos[0]) % 2 == 0 ]
		self._hit_list = []
		self._move_idx = 0
		self._hit_idx = 1
		self._moves = {3:(1,0), 2:(-1,0), 0:(0,1), 1:(0,-1)}
		
	def add_vectors(self, pos1, pos2):
		"""
		Used to add components of vectors when moving around board.
		"""
		return (pos1[0] + pos2[0], pos1[1] + pos2[1])
		
	def scalar(self, pos, scalar):
		"""
		Multiplies the entries in a vector by a scalar.
		"""
		return (pos[0] * scalar, pos[1] * scalar)
		
	def update_hit_list(self):
		"""
		Checks if any of the hits in the hit_list correspond to sunk ships.
		If so they will be removed from the list.
		"""
		temp_list = list(self._hit_list)

		for hit in temp_list:
			if self._board.get_status(hit) != HIT:
				self._hit_list.remove(hit)
	
		
	def random_strike(self):
		"""
		Randomly strikes a position from the checkerboard grid.
		"""
		self._move_idx = 0
		self._hit_idx = 1
		pos = random.choice(self._checkers)
		self._checkers.remove(pos)
		self._fleet.check_for_damages([pos])
		status = self._board.get_status(pos)
		if status == HIT:
			self._hit_list.append(pos)
		elif status != MISS:
			self.update_hit_list()
		
		
	def strike(self):
		"""
		If a ship has been hit the strategy is to continue to hit until the 
		ship is sunk. A ship is sunk when its identity is revealed in the 
		board status.
		"""
		if self._hit_list == []:
			return
		
		# the following loop will repeat until the next target is found. 	
		available = False
		while available == False:   # find the next available target by moving around a known hit
			next_hit = self.add_vectors(self._hit_list[0], self.scalar(self._moves[self._move_idx], self._hit_idx))
			if next_hit[0] in range(0,10) and next_hit[1] in range(0,10):  # this says the target is on the board
				if self._board.get_status(next_hit) == HIDDEN:   			# this says the target's status is still unknown
					available = True
				else:
					self._hit_idx = 1
					self._move_idx = (self._move_idx + 1) % 4     # this looks for a target in a different direction
			else:
				self._hit_idx = 1
				self._move_idx = (self._move_idx + 1) % 4     # this looks for a target in a different direction
				
		if next_hit in self._checkers:
			self._checkers.remove(next_hit)
			
		self._fleet.check_for_damages([next_hit])
		status = self._board.get_status(next_hit)
		
		if status == HIT:
			self._hit_list.append(next_hit)
			self._hit_idx += 1              # Keep going in this direction
		elif status == MISS:
			self._move_idx = (self._move_idx + 1) % 4   # Change directions
			self._hit_idx = 1
		else:
			self.update_hit_list()
			self._hit_idx = 1
			
	def take_turn(self):
		"""
		Check to see if there are any hit ships in the list.
		If so, then hit around the first element in the list by using strike algorithm.
		If not, randomly choose a target from the checker board pattern.
		"""
		# print self._hit_list
		if self._hit_list == []:
			self.random_strike()
		else:
			self.strike()
		self.update_hit_list()
				
							
########  Helper Functions         ##############################			
			
					
def create_ship(board = Board(), code = "A"): 
	"""
    Generates a set containing all possible places a ship of type code could go
    on the given board and then randomly chooses one of these to be the position of the ship.
    It updates the used and unused squares on the board and
    returns the helm position of the ship and orientation of the ship
    """
  	avail = []
	ship_length = Ship[code][1]
	
	for row in range(0, board.get_size()):
		for col in range(0,board.get_size() + 1 - ship_length):
			poss = []
			for idx in range(0, ship_length):
				poss.append((row,col + idx))
			if set(poss) <= board.get_unused():
				avail.append(poss)
	for col in range(0, board.get_size()):
		for row in range(0,board.get_size() + 1 - ship_length):
			poss = []
			for idy in range(0,ship_length):
				poss.append((row + idy,col))
			if set(poss) <= board.get_unused():
				avail.append(poss)
	ship_span = random.choice(avail) 
	board.remove_unused(ship_span)
	board.update_used(ship_span)
	# print ship_span
	ship_orientation = ship_span[1][0] - ship_span[0][0]
	ship_helm = ship_span[0]
	return 	ship_helm, ship_orientation
    
def draw_occupied_board(fleet = Fleet()):
	"""
	Shows the location of all ships in the fleet as a graphical
	display.
	"""
	show_board = Board(fleet.get_player())
	for ship in fleet.get_fleet().itervalues():
		if ship.get_location() != None:
			for pos in ship.get_location():
				show_board.update_status(pos,ship.get_code())
	print show_board
	return show_board
	
def player_set_up(board = Board(), fleet = Fleet()):
	"""
	Asks player to move ships onto the board
	"""

	player =  board.get_player()
	print
	print
	print
 	print "#########################################################################"
	print "#	"                                                                                                                                           
	print "#	          Welcome to Battleship: Your Player  vs. The Computer "                                          
	print "#"                                                                                                                                           
	print "#########################################################################"
	print
	print
	print " Hello " + str(player) + ". It is time for you to place your ships on the board."
	print " You have 5 ships: \n 'A' = an Aircraft carrier (5 spaces), \n 'B' = a Battleship (4 spaces), "
	print " 'D' = a Destroyer (3 spaces), \n 'S' = Submarine (3 spaces), and \n 'P' = a Patrol Boat (2 spaces)"
	print
	print "Look at your board below. You have 10 rows labeled 0 - 9 and 10 columns labeled 0 - 9."
	print "You will place your ships by entering the following information separated only by spaces. Example: A 1 2 0."
	print " At the prompt, enter the ship you wish to place. You may reenter any ship multiple times. When all ships"
	print "    have been placed and you are happy with your arrangement, type 'x to exit setup and begin the game."

	print board
	set_up = True
	placed_ships = 0
	while set_up == True:
		print "      <shipcode: A, B, D, S, P>  <row: 0-9>  <column:0-9>  <orientation:0=horizontal,1=vertical>   "
		print "       remember to separate each letter or number using only spaces. Press enter when done. Press 'q' to quit and 'x' to exit setup."
		your_resp = raw_input()
		if your_resp == 'q':
			sys.exit(0)
			return
			
		if your_resp == 'x' and placed_ships < 5:
			print "You do not have all of your ships placed. Please reenter your response."
		elif your_resp == 'x':
			print "Set up complete"	
			set_up = False
		elif your_resp == "":
			print "You must enter some response."
		else:	
			response = your_resp.split()
			if len(response) < 4:
				print "Re-enter your response as a 4 symbol code."
			else:
				code = response[0]
				pos = (int(response[1]), int(response[2]))
				ori = int(response[3])
				print code, pos, ori
				if code not in Ship.iterkeys():
					print "Letter symbol must be A B D S or P. Re-enter response."
				elif len(response) < 4:
					print " Re-enter your response as a 4 symbol code, each symbol separated by a space like: B 0 4 1."
				elif pos not in board.get_grid():
					print "Row and Column values must be in 0-9.  Re-enter response."
				elif ori not in [0,1]:
					print "Orientation is 0 for horizontal and 1 for vertical.  Re-enter response."
				else:
					success = fleet.get_fleet()[code].move(pos, ori)
				draw_occupied_board(fleet)
		placed_ships = 0
		for ship in fleet.get_fleet().itervalues():
			if ship.get_location() != None:
				placed_ships += 1
		if placed_ships == 5:
			print "You have placed all of your ships. You may move a ship or enter x when you are ready to continue."
			
	return
	
def player_test_set_up(board = Board(), fleet = Fleet(), test = None):
	"""
	This receives a placement for the ships and puts the players ships there
	test is a list of the form ['A 1 0 1', 'B 3 4 0', ect.... for all 5 ships]
	"""
	if len(test) != 5:
		print "insufficient data"
		return
	for your_resp in test:
		response = your_resp.split()
		if len(response) < 4:
			print "Re-enter your response as a 4 symbol code."
			return
		else:
			code = response[0]
			pos = (int(response[1]), int(response[2]))
			ori = int(response[3])
			print code, pos, ori
			if code not in Ship.iterkeys():
				print "Letter symbol must be A B D S or P. Re-enter response."
				return
			elif pos not in board.get_grid():
				print "Row and Column values must be in 0-9.  Re-enter response."
				return
			elif ori not in [0,1]:
				print "Orientation is 0 for horizontal and 1 for vertical.  Re-enter response."
				return
			else:
				fleet.get_fleet()[code].move(pos, ori)

		placed_ships = 0
		for ship in fleet.get_fleet().itervalues():
			if ship.get_location() != None:
				placed_ships += 1
		if placed_ships == 5:
			print "You have placed all of your ships. "
			draw_occupied_board(fleet)

########  Play the Game                ##############################
####### Step 1 - pass out the pieces to each player
##

print "What is your name? >>  ",
your_name = raw_input()
print
print "Hello " + your_name + ". Welcome to Battleship"

my_player = Player(your_name)
my_board = Board(my_player)
my_fleet = Fleet(my_board)

######## Step 2 - place players ship on the board
print
##################  For  Testing  ##########################################
# uncomment the next two lines and comment out player_set_up to auto run the player set up
#test1 = ['A 4 3 1', 'B 0 0 1', 'D  9 2 0', 'S 2 9 1', 'P 0 8 0']
#player_test_set_up(my_board, my_fleet, test1)
######################################################################
player_set_up(my_board, my_fleet)
print


enemy = Player("The Enemy")
enemy_board = Board(enemy)
enemy_fleet = Fleet(enemy_board, False)

######### If you want to cheat, uncomment the following line and the enemy board will
######### be displayed with its ships placed.
# draw_occupied_board(enemy_fleet)  

####### Step 3 - give the computer an algorithm to follow to find the player's ships
enemy_strategy = Strategy(my_board, my_fleet)

####### Step 4 - begin taking turns - game will terminate when a fleet is destroyed
turn = 0
while my_fleet.get_health > 0 and enemy_fleet.get_health > 0:
	
	if turn % 2 == 0:
		print enemy_board
		next_hit = ()
		while next_hit == ():
			print str(my_player) + ",  please enter a row (0-9) and column (0-9) separated only by a space."
			print ">> ",
			your_response = raw_input()
			
			entry = your_response.split()

			if len(entry) != 2:
				print "Please enter exactly two numbers"
			else:
				entry = (int(entry[0]), int(entry[1]))
				if entry[0] not in range(0,10) or entry[1] not in range(0,10):
					print "Please enter two numbers between 0 and 9."
				elif enemy_board.get_status(entry) != HIDDEN:
					print "Please choose a point not already chosen."
				else:
					next_hit = entry
		
		enemy_fleet.check_for_damages([next_hit])
		turn += 1	
			
	else:		
		enemy_strategy.take_turn()
		turn += 1
