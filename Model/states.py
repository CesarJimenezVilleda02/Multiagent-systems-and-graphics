from enum import Enum


class state(Enum):
      # Advance represents movement at normal speed
  ADVANCE = 1
  # Stop represents no movement
  STOP = 2
  # Moving to right lane, no forward movement happens, is equal to stop
  MOVE_RIGHT = 3
  # Moving to left lane, no forward movement happens, is equal to stop
  MOVE_LEFT = 4
  # Car is broken and cannot move
  BREAK = 5
  # Car starts transition to stop
  DECELERATE = 6
  # Car starts transition to normal speed
  ACCELERATE = 7
  # Car is out of bounds
  ELIMINATE = 8
  # Car spawn
  SPAWN = 9