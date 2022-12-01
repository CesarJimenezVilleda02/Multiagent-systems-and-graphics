# Importamos las clases que se requieren para manejar los agentes (Agent) y su entorno (Model).
# Cada modelo puede contener múltiples agentes.
from mesa import Agent, Model 

# Con ''SimultaneousActivation, hacemos que todos los agentes se activen ''al azar''.
from mesa.time import SimultaneousActivation

# Haremos uso de ''DataCollector'' para obtener información de cada paso de la simulación.
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid

# matplotlib lo usaremos crear una animación de cada uno de los pasos del modelo.
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

# Importamos los siguientes paquetes para el mejor manejo de valores numéricos.
import numpy as np
import pandas as pd
from random import randrange
from enum import Enum

# Definimos otros paquetes que vamos a usar para medir el tiempo de ejecución de nuestro algoritmo.
import time
import datetime

import final_model, states, final_data_collector
from states import state

class Car_agent(Agent):
  def __init__(self, unique_id, model):
    super().__init__(unique_id, model)
    # CAR STARTS STOPPED
    self.state = states.state.SPAWN
    self.next_state = None
    self.speed = 0
    self.max_speed = 3
    self.waiting = 0
    self.moves=0
  
  def step(self):
    self.max_speed = self.model.speeds[self.pos[0]][self.pos[1]]

    self.moves+=1
    if self.pos[1] == self.model.road_length - 1:
      self.state = state.ELIMINATE
      return
    
    # CAR BREAKS
    chance = randrange(1500/ (self.pos[0] + 1))
    # Contiguos cars cannot break and a car in the simulation will break after two minutes
    if chance == 0 and self.model.step_number > 40 and self.model.road_length / 3 < self.pos[1]:
      self.engine_fail()
      return

    # Car is broken so we dont perform any other action
    if self.state == states.state.BREAK:
      if self.speed > 0:
        self.speed -= 1
        self.move()
      return
    
    # TURNING
    # We check if the car is currently waiting in line and if it is at the front, we make it try to turn, else it waits
    if self.state == states.state.STOP and self.is_at_front():
      if self.can_move_sides():
        self.move_sides()
        self.speed = 0
        return
    
    # MOVING
    if self.can_accelerate():
      self.accelerate()
      if self.speed == self.max_speed:
        self.state = states.state.ADVANCE
        return
    elif self.has_to_decelerate():
      self.decelerate()
      if self.speed == 0:
        self.state = states.state.STOP
        self.model.total_stops+=1
        return
    
    if self.can_move():
      self.move()
      return
    else:
      self.speed = 0
      self.state = states.state.STOP
      self.model.total_stops+=1
      return

  def advance(self):
    if self.state == states.state.ELIMINATE:
      self.model.finished_cars+=1
      self.model.total_moves+= self.moves

      self.road_end()

  # CAR IS ELIMINATED FROM SIMULATION
  def road_end(self):
    #self.model.grid.place_agent(self, (self.pos[0], self.road_length - 1))
    self.state = state.ELIMINATE
    self.model.to_remove.append(self)
    return

  # CHECK IF THE CAR IS THE FIRST IN LINE TO TURN
  def is_at_front(self):
    for i in range(1, 3):
      if self.is_in_bounds(self.pos[1]+i) and not self.model.grid.is_cell_empty((self.pos[0], self.pos[1]+i)) and  self.model.grid[self.pos[0]][self.pos[1]+i].state == state.BREAK:
        return True

    return False

  # MOVE CAR TO ANY CONTIGOUS LANE WHERE SPACE IS AVAILABLE
  def move_sides(self):
    # leftmost lane
    if self.pos[0] == 0:
      if self.can_move_side(self.pos[0] + 1):
        self.move_to_lane(self.pos[0] + 1)
        self.state = state.MOVE_RIGHT
    # rightmost lane
    elif self.pos[0] == self.model.number_road - 1:
      if self.can_move_side(self.pos[0] - 1):
        self.move_to_lane(self.pos[0] - 1)
        self.state = state.MOVE_LEFT
    # central lane
    else:
      # the order affects the priority a car gives to moving to a certain lane
      if self.can_move_side(self.pos[0] - 1):
        self.move_to_lane(self.pos[0] - 1)
        self.state = state.MOVE_RIGHT
      elif self.can_move_side(self.pos[0] + 1):
        self.move_to_lane(self.pos[0] + 1)
        self.state = state.MOVE_LEFT

  # MOVE CAR TO LANE
  def move_to_lane(self, lane):
    self.model.grid.move_agent(self, (lane, self.pos[1]+1))

  # CHECK IF CAN MOVE TO A SPECIFIC LANE
  def can_move_sides(self):
    # leftmost lane
    if self.pos[0] == 0:
      if self.can_move_side(self.pos[0] + 1):
        return True
    # rightmost lane
    elif self.pos[0] == self.model.number_road - 1:
      if self.can_move_side(self.pos[0] - 1):
        return True
    # central lane
    else:
      if self.can_move_side(self.pos[0] + 1):
        return True
      elif self.can_move_side(self.pos[0] - 1):
        return True
    return False

  # CHECK IF CAN MOVE TO ANY CONTIGOUS LANE
  def can_move_side(self, lane):
    for i in range(-1, int(self.calc_braking_distance(self.model.speeds[lane][self.pos[1]-1]))):
      # Check if car behind is broken - then move
      if self.is_in_bounds(self.pos[1]-i) and not self.model.grid.is_cell_empty((lane, self.pos[1]-i)) and self.model.grid[lane][self.pos[1]-i].state == state.BREAK:
        return True
      # Check if car behind has a speed that allows moving in front of it
      elif self.is_in_bounds(self.pos[1]-i) and (not self.model.grid.is_cell_empty((lane, self.pos[1]-i)) 
      and self.calc_braking_distance(self.model.grid[lane][self.pos[1]-i].speed) + self.pos[1]-i <= self.pos[1]):
        return False
      elif self.is_in_bounds(self.pos[1]-i) and not self.model.grid.is_cell_empty((lane, self.pos[1]-i)):
        return False

    return True

  # CHECK IF CAN MOVE
  def can_move(self):
    for i in range(1, self.speed):
      # Looks for other car in the front safe braking distance
      if self.is_in_bounds(self.pos[1]+i) and not self.model.grid.is_cell_empty((self.pos[0], self.pos[1]+i)):
        return False
    
    return True
  
  # CHECK IF CAN ACCELERATE
  def can_accelerate(self):
    if self.speed == self.max_speed:
      return False
    
    next_speed = self.speed + 1
    for i in range(1, self.calc_braking_distance(next_speed) + next_speed):
      # Looks for other car in the front safe braking distance
      if self.is_in_bounds(self.pos[1]+i) and not self.model.grid.is_cell_empty((self.pos[0], self.pos[1]+i)):
        return False
    
    return True

  # CHECK IF HAS TO DECELERATE
  def has_to_decelerate(self):
    for i in range(1, self.calc_braking_distance(self.speed) + 1):
      # Looks for other car in the front safe braking distance
      if self.is_in_bounds(self.pos[1]+i) and not self.model.grid.is_cell_empty((self.pos[0], self.pos[1]+i)):
        return True
    
    return False

  # DETERMINE DECELERATION DISTANCE FOR SAFE BRAKING
  def calc_braking_distance(self, curr_speed):
    distance = 0;
    speed = curr_speed
    while speed > 0:
      distance += speed
      speed -= 1
    # We add one because the other car needs it to start decelerating
    return distance + 1

  # MOVE AGENT DEPENDING ON SPEED
  def move(self):
    if self.is_in_bounds(self.pos[1]+self.speed):
      self.model.grid.move_agent(self, (self.pos[0], self.pos[1]+self.speed))
    else:
      self.state = states.state.ELIMINATE
  
  # CAR FAILS - NO CAR CAN FAIL IF A NEARBY CAR HAS ALREADY FAILED
  def engine_fail(self):
    neighbors=self.model.grid.get_neighbors((self.pos[0], self.pos[1]),True, False,5)
    for agent in neighbors:
      if agent.state == states.state.BREAK:
        return
    self.state = states.state.BREAK
    self.reduce_speed()

  def reduce_speed(self):
    if self.pos[0]>0:
      for i in range(self.pos[1]):
        if  self.model.speeds[self.pos[0]-1][i]==1:
            return
        self.model.speeds[self.pos[0]-1][i]=self.model.speeds[self.pos[0]-1][i]-1
    elif self.pos[0]<2:
     
      for i in range(self.pos[1]):
        if  self.model.speeds[self.pos[0]+1][i]==1:
            return
        self.model.speeds[self.pos[0]+1][i]=self.model.speeds[self.pos[0]+1][i]-1


  # CHECK IF POSITION IS A VALID ROAD LOCATION
  def is_in_bounds(self, pos):
    return pos >= 0 and pos <= self.model.road_length - 1

  # DECELERATE CAR
  def decelerate(self):
    self.state = states.state.DECELERATE
    self.speed -= 1

  # ACCELERATE CAR
  def accelerate(self):
    self.state = states.state.ACCELERATE
    self.speed += 1