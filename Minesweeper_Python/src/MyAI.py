# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action

GLOBAL_UNDEF = -1
IS_MINE = 9

class TileNode:

	def __init__(self, uncovered=GLOBAL_UNDEF, eff_label=GLOBAL_UNDEF, adj_tiles=8, is_marked = False):
		self._uncovered = uncovered
		self._effective_label = eff_label
		self._adj_cov_tiles = adj_tiles
		self._is_marked = is_marked

	def uncover(self,uncovered_val): 
		self._uncovered = uncovered_val
	def up_eff(self, adj_mines): 
		self._effective_label = self._uncovered - adj_mines if self._uncovered != GLOBAL_UNDEF else GLOBAL_UNDEF
	def up_adj(self, adj_tiles): 
		self._adj_cov_tiles = adj_tiles
	def mark(self):
		self._is_marked = True
		self._uncovered = IS_MINE

	def get_unc(self):  return self._uncovered
	def get_label(self): return self._effective_label
	def get_adj(self): return self._adj_cov_tiles
	def get_flg(self): return self._is_marked


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self._mines = totalMines
		self._rows = rowDimension
		self._cols = colDimension
		self._dir = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

		self._grid = [[TileNode() for _ in range(colDimension)] for _ in range(rowDimension)]
		self._start(startX, startY)

		self._last_move = (startX, startY)
		# _uncovering is a list of all nodes to be uncovered (we confirmed are 100% already)
		self._uncovering = []
		# _updates stores the updates of the recently uncovered nodes (until all nodes have been uncovered)
		self._updates = []

		# _unc_f is the uncovered frontier (nodes uncovered next to covered nodes), _cov_f is the covered frontier
		self._unc_f = []
		self._cov_f = []
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

	def _start(self, startX, startY):
		self._grid[startX][startY].uncover(0)
		self._grid[startX][startY].up_eff(0)
		self._update_adj()

	def _update_adj(self):
		for r in range(self._rows):
			for c in range(self._cols):
				covered = 0
				marked = 0
				for dr, dc in self._dir:
					if self._inbound(r+dr, c+dc) and self._grid[r+dr][c+dc].get_unc() in (GLOBAL_UNDEF, IS_MINE):
						covered += 1
					if self._inbound(r+dr, c+dc) and self._grid[r+dr][c+dc].get_flg():
						marked += 1
				self._grid[r][c].up_adj(covered)
				self._grid[r][c].up_eff(marked)

	def _inbound(self, x, y):
		return True if 0 <= x < self._rows and 0 <= y < self._cols else False

	# Frontier searching fucntions
	def _find_frontier(self):
		pass

	def _adj_covered(self, row, col):
		num_covered = 0
		for dr, dc in self._dir:
			if self._inbound(row+dr, col+dc) and self._grid[row+dr][col+dc].get_unc() in (GLOBAL_UNDEF, IS_MINE):
				num_covered += 1
		return num_covered

	
	# Updating grid functions
	def _uncover_adj(self, row, col):
		'''adds all adj tiles to list of tiles to uncover'''
		for dr, dc in self._dir:
			if self._inbound(row+dr, col+dc):
				self._uncover_tile(row+dr, col+dc)

	def _flag_adj(self, row, col):
		'''covers all the adj tiles since they're all mines (eff_label = adj_unc)'''
		for dr, dc in self._dir:
			if self._inbound(row+dr, col+dc):
				self._flag_tile(row+dr, col+dc)

	def _uncover_tile(self, row, col):
		'''uncovers a specific tile'''
		if self._grid[row][col].get_unc() == GLOBAL_UNDEF and (row, col) not in self._uncovering:
			self._uncovering.append((row, col))

	def _flag_tile(self, row, col):
		'''flags a specific tile'''
		if not self._grid[row][col].get_flg() and self._grid[row][col].get_unc() == GLOBAL_UNDEF:
			self._grid[row][col].mark()

		
	# Action object should represent the x and y coordinate of the tile to be uncovered
	def getAction(self, number: int) -> "ActionObject":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		
		# Grid updates from last move (number is tile number of last move)
		# print(f'last move: {self._last_move}, number: {number}')
		self._grid[self._last_move[0]][self._last_move[1]].uncover(number)
		self._update_adj()
		# FOR TESTING/DEBUGGING PURPOSES
		# self._print_board()

		# Add more moves to uncover given new update on board
		for r in range(self._rows):
			for c in range(self._cols):
				if self._grid[r][c].get_label() == 0:
					self._uncover_adj(r, c)
				elif self._grid[r][c].get_label() == self._adj_covered(r, c):
					# print(f'flagging all at ({r}, {c})')
					# print(f'label of ({r}, {c}): {self._grid[r][c].get_label()}')
					self._flag_adj(r, c)
		
		# FOR TESTING/DEBUGGING PURPOSES
		# print('currently uncovering:', self._uncovering)
		# _ = input('Press any key to continue...\n')

		# Will uncover move if there is a move to be uncovered
		if self._uncovering != []:
			self._last_move = self._uncovering.pop(0)
			return Action(AI.Action.UNCOVER, self._last_move[0], self._last_move[1])
		return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################


	# FOR DEBUGGING PURPOSES (TO VISUALIZE THE BOARD)
	def _print_board(self):
		print(f"    {' '.join([f'   {col_num+1}  ' for col_num in range(self._cols)])}")
		for row_num in range(self._rows):
			print(f'{row_num+1} | ', end='')
			for col_num in range(self._cols):
				marking = self._grid[row_num][col_num].get_unc()
				if marking == GLOBAL_UNDEF: marking = '*'
				elif marking == IS_MINE: marking = 'M'
				else: marking == str(marking)

				eff_label = self._grid[row_num][col_num].get_label()
				if eff_label in (GLOBAL_UNDEF, IS_MINE): eff_label = ' '
				else: eff_label = str(eff_label)

				adj_tiles = str(self._grid[row_num][col_num].get_adj())

				print(f' {marking}:{eff_label}:{adj_tiles} ', end='')
			print()
