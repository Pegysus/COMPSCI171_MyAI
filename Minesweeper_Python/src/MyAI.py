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

import itertools
import time
import random

# FOR TESTING/DEBUGGING PURPOSES
import os

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
		# print(rowDimension, colDimension)
		# print(totalMines)
		# print(startX, startY)

		self._mines = totalMines
		self._rows = rowDimension
		self._cols = colDimension
		self._dir = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

		self._grid = [[TileNode() for _ in range(rowDimension)] for _ in range(colDimension)]
		self._start(startX, startY)

		self._last_move = (startX, startY)
		# _uncovering is a list of all nodes to be uncovered (we confirmed are 100% already)
		self._uncovering = []
		# _updates stores the updates of the recently uncovered nodes (until all nodes have been uncovered)
		self._updates = []

		# _unc_f is the uncovered frontier (nodes uncovered next to covered nodes), _cov_f is the covered frontier
		self._all_cov_f = []
		self._t_cov_f = []
		self._all_unc_f = []
		self._t_unc_f = []

		self._unc_f = []
		self._cov_f = []

		self._pos_models = []
		self._all_models = []
		self._max_model_length = 20
		self._guessing = []

		# Time tracking
		self._start_time = int(time.time())
		self._time_diff = 0

		# FOR TESTING/DEBUGGING PURPOSES
		self.clear = lambda: os.system('clear')

		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

	def _start(self, startX, startY):
		self._grid[startX][startY].uncover(0)
		self._grid[startX][startY].up_eff(0)
		self._update_adj()

	def _update_adj(self):
		for c in range(self._cols):
			for r in range(self._rows):
				self._update_tile(c, r)
	
	def _update_tile(self, c, r):
		covered = 0
		marked = 0
		for dc, dr in self._dir:
			if self._inbound(c+dc, r+dr) and self._grid[c+dc][r+dr].get_unc() == GLOBAL_UNDEF:
				covered += 1
			if self._inbound(c+dc, r+dr) and self._grid[c+dc][r+dr].get_flg():
				marked += 1
		self._grid[c][r].up_adj(covered)
		self._grid[c][r].up_eff(marked)

	def _inbound(self, x, y):
		return True if 0 <= x < self._cols and 0 <= y < self._rows else False


	# TODO: frontier search optimization #2 (if expert mode still isn't optimized enough): search for all current frontiers
	# as there can be multiple frontiers of different length. Then pick the one of smallest length and search there
	# If smallest length frontier doesn't yield any results, go to next largest, etc. etc.
	# (Hopefully it's more optimal?)
	def _find_all_cov_frontiers(self):
		self._all_cov_f = []
		self._all_unc_f = []

		for c in range(self._cols):
			for r in range(self._rows):
				if self._grid[c][r].get_adj() > 0 and self._grid[c][r].get_unc() not in (GLOBAL_UNDEF, IS_MINE) \
					and not any((c, r) in f for f in self._all_unc_f):

						self._t_unc_f = []
						self._t_cov_f = []
						self._total_f(c,r)
						self._all_cov_f.append(self._t_cov_f)
						self._all_unc_f.append(self._t_unc_f)
		
		#FOR TESTING/DEBUGGING PURPOSES
		# print('# of frontiers:', len(self._all_cov_f))
		# for i in range(len(self._all_cov_f)):
		# 	print(f'\tfrontier {i} start: {self._all_cov_f[i][0]}')
		# 	print(f'\t\t{self._all_cov_f[i]}')

	def _total_f(self, c, r):
		self._t_unc_f.append((c,r))
		self._cov_f_search(c,r)
	def _cov_f_search(self, c, r):
		for dc, dr in self._dir:
			if self._inbound(c+dc, r+dr) and self._grid[c+dc][r+dr].get_unc() == GLOBAL_UNDEF \
					and (c+dc, r+dr) not in self._t_cov_f and len(self._t_cov_f) < self._max_model_length \
					and not any((c+dc, r+dr) in f for f in self._all_cov_f):

				self._t_cov_f.append((c+dc, r+dr))
				self._unc_f_search(c+dc,r+dr)
	def _unc_f_search(self, c, r):
		for dc, dr in self._dir:
			if self._inbound(c+dc, r+dr) and self._grid[c+dc][r+dr].get_unc() not in (GLOBAL_UNDEF, IS_MINE) \
				and (c+dc, r+dr) not in self._t_unc_f and not any((c+dc, r+dr) in f for f in self._all_unc_f):

				self._t_unc_f.append((c+dc, r+dr))
				self._cov_f_search(c+dc,r+dr)

	def _adj_covered(self, col, row):
		num_covered = 0
		for dc, dr in self._dir:
			if self._inbound(col+dc, row+dr) and self._grid[col+dc][row+dr].get_unc() in (GLOBAL_UNDEF, IS_MINE):
				num_covered += 1
		return num_covered

	
	# Model Checking implementation
	def _model_check(self):
		self._pos_models = []

		bit_strings = [''.join(i) for i in itertools.product('01', repeat=len(self._cov_f))]

		# FOR TESTING/DEBUGGING PURPOSES
		# print('length of covered frontier:', len(self._cov_f), 'length of unc frontier:', len(self._unc_f))

		self._all_models = [[int(node) for node in model] for model in bit_strings]
		for model in self._all_models:
			self._cur_time = int(time.time())
			self._time_diff = self._cur_time - self._start_time
			if self._time_diff > 280:
				return

			self._check_model(model)

		# FOR TESTING/DEBUGGING PURPOSES
		# print('checking model, cur time:', self._time_diff)
		# print('possible models:')
		# for model in self._pos_models:
		# 	print(f'\t{model}')
		
		num_zeroes = [0 for _ in range(len(self._cov_f))]
		for model in self._pos_models:
			for i in range(len(model)):
				if model[i] == 0:
					num_zeroes[i] += 1

		# FOR TESTING/DEBUGGING PURPOSES
		# print('possible models: ', self._pos_models)
		# print('num zeroes:', num_zeroes)

		for i in range(len(num_zeroes)):
			if num_zeroes[i] == len(self._pos_models) and len(self._pos_models) != 0:
				self._uncover_tile(*self._cov_f[i])
			# elif num_zeroes[i] == 0:
			# 	self._flag_tile(*self._cov_f[i])
		if self._uncovering == []:

			# FOR TESTING/DEBUGGING PURPOSES
			# print('have to guess')
			
			maxi = max(num_zeroes)
			guesses = []
			for i in range(len(num_zeroes)):
				if num_zeroes[i] == maxi:
					guesses.append(self._cov_f[i])

			self._guess_tile(*guesses[random.randint(0, len(guesses)-1)])

	def _check_model(self, model):
		for col, row in self._unc_f:
			check_model_adj = 0
			for dc, dr in self._dir:
				if self._inbound(col+dc, row+dr) and (col+dc, row+dr) in self._cov_f and model[self._cov_f.index((col+dc, row+dr))] == 1:
					check_model_adj += 1
			if check_model_adj != self._grid[col][row].get_label():
				return
		self._pos_models.append(model)

	
	# Updating grid functions
	def _uncover_adj(self, col, row):
		'''adds all adj tiles to list of tiles to uncover'''
		for dc, dr in self._dir:
			if self._inbound(col+dc, row+dr):
				self._uncover_tile(col+dc, row+dr)

	def _flag_adj(self, col, row):
		'''covers all the adj tiles since they're all mines (eff_label = adj_unc)'''
		for dc, dr in self._dir:
			if self._inbound(col+dc, row+dr):
				self._flag_tile(col+dc, row+dr)

	def _uncover_tile(self, col, row):
		'''uncovers a specific tile'''
		if self._grid[col][row].get_unc() == GLOBAL_UNDEF and (col, row) not in self._uncovering:
			self._uncovering.append((col, row))
	def _guess_tile(self, col, row):
		'''guesses a specific tile'''
		if self._grid[col][row].get_unc() == GLOBAL_UNDEF and (col, row) not in self._uncovering:
			self._guessing.append((col, row))

	def _flag_tile(self, col, row):
		'''flags a specific tile'''
		if not self._grid[col][row].get_flg() and self._grid[col][row].get_unc() == GLOBAL_UNDEF:
			self._grid[col][row].mark()
			self._mines -= 1
			self._update_tile(col, row)

	def _uncover_remaining(self):
		for c in range(self._cols):
			for r in range(self._rows):
				self._uncover_tile(c, r)

		
	# Action object should represent the x and y coordinate of the tile to be uncovered
	def getAction(self, number: int) -> "ActionObject":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		

		# FOR TESTING/DEBUGGING PURPOSES
		# Grid updates from last move (number is tile number of last move)
		# self.clear()
		# print(f'last move: {self._last_move}, number: {number}')

		self._grid[self._last_move[0]][self._last_move[1]].uncover(number)
		self._update_adj()

		self._cur_time = int(time.time())
		self._time_diff = self._cur_time - self._start_time

		if self._time_diff > 280:
			return Action(AI.Action.LEAVE)

		# FOR TESTING/DEBUGGING PURPOSES
		# self._print_board()

		# flag everything that can be flagged
		for c in range(self._cols):
			for r in range(self._rows):
				if self._grid[c][r].get_label() == self._grid[c][r].get_adj() and self._grid[c][r].get_label() != 0:
					# FOR TESTING/DEBUGGING PURPOSES
					# print(f'flagging all at ({c}, {r})')
					# print(f'label of ({c}, {r}): {self._grid[c][r].get_label()}')
					self._flag_adj(c, r)
		self._update_adj()

		if self._mines == 0:
			self._uncover_remaining()
			if self._uncovering != []:
				self._last_move = self._uncovering.pop(0)
				return Action(AI.Action.UNCOVER, self._last_move[0], self._last_move[1])
			return Action(AI.Action.LEAVE)

		# Add more moves to uncover given new update on board
		for c in range(self._cols):
			for r in range(self._rows):
				if self._grid[c][r].get_label() == 0:
					self._uncover_adj(c, r)
		
		if self._uncovering == []:
			# FOR TESTING/DEBUGGING PURPOSES
			# print('basic algorithm found nothing, using frontier/model checking...')

			self._find_all_cov_frontiers()

			# FOR TESTING/DEBUGGING PURPOSES
			# print('currently uncovering:', self._uncovering)
			# _ = input('Press any key to continue...\n')
			for i in range(len(self._all_cov_f)):
				self._guessing = []
				self._cov_f = self._all_cov_f[i]
				self._unc_f = self._all_unc_f[i]
				# print('current uncover frontiers: ', self._unc_f)
				# print('current covered frontiers: ', self._cov_f)

				self._model_check()

			# _ = input('Press any key to continue...\n')

		if self._time_diff > 280:
			return Action(AI.Action.LEAVE)

		# FOR TESTING/DEBUGGING PURPOSES
		# print('current uncover frontiers: ', self._unc_f)
		# print('current covered frontiers: ', self._cov_f)
		# print('currently uncovering:', self._uncovering)
		# _ = input('Press any key to continue...\n')
		

		# Will uncover move if there is a move to be uncovered
		if self._uncovering != []:
			self._last_move = self._uncovering.pop(0)
			return Action(AI.Action.UNCOVER, self._last_move[0], self._last_move[1])
		elif self._guessing != []:
			self._last_move = self._guessing.pop(0)
			return Action(AI.Action.UNCOVER, self._last_move[0], self._last_move[1])
		return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################


	# FOR DEBUGGING PURPOSES (TO VISUALIZE THE BOARD)
	# def _print_board(self):
	# 	print(f"    {' '.join([f'   {row_num+1}  ' for row_num in range(self._rows)])}")
	# 	for col_num in range(self._cols):
	# 		print(f'{col_num+1}'.ljust(3) + '| ', end='')
	# 		for row_num in range(self._rows):
	# 			marking = self._grid[col_num][row_num].get_unc()
	# 			if marking == GLOBAL_UNDEF: marking = '*'
	# 			elif marking == IS_MINE: marking = 'M'
	# 			else: marking == str(marking)

	# 			eff_label = self._grid[col_num][row_num].get_label()
	# 			if eff_label in (GLOBAL_UNDEF, IS_MINE): eff_label = ' '
	# 			else: eff_label = str(eff_label)

	# 			adj_tiles = str(self._grid[col_num][row_num].get_adj())

	# 			print(f' {marking}:{eff_label}:{adj_tiles} ', end='')
	# 		print()
