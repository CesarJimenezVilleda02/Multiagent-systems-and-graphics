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
  
def get_grid_server(model):
  agents = []

  for x in range (model.grid.width):
    for y in range (model.grid.height):
      if not model.grid.is_cell_empty((x, y)):
        agent = model.grid[x][y]
        # # agent_id, state, speed, position
        agents.append([agent.unique_id, agent.state, agent.speed, agent.pos[0], agent.pos[1]])
        # agents.append(agent.actual_car)

  return agents

def get_grid(model):
      # define color map 
  color_map = {1: np.array([220, 220, 220]), # road
              2: np.array([255, 51, 51]), # red
              3: np.array([128, 255, 0]), # green
              4: np.array([255, 128, 0]), # orange
              5: np.array([0, 0, 0]), # broken
              6: np.array([255, 255, 0]), # decelerate
              7: np.array([153, 204, 255]),} # accelerate 

  grid = np.ndarray(shape=(model.grid.width, model.grid.height, 3), dtype=int)
  for x in range (model.grid.width):
    for y in range (model.grid.height):
      if model.grid.is_cell_empty((x, y)):
        grid[x][y] = color_map[1]
      else:
        content = model.grid[x][y]
        # color by state of car
        if content.state == state.STOP:
          grid[x][y] = color_map[2]
        elif content.state == state.ADVANCE:
          grid[x][y] = color_map[3]
        elif content.state == state.MOVE_RIGHT:
          grid[x][y] = color_map[4]
        elif content.state == state.MOVE_LEFT:
          grid[x][y] = color_map[4]
        elif content.state == state.BREAK:
          grid[x][y] = color_map[5]
        elif content.state == state.DECELERATE:
          grid[x][y] = color_map[6]
        elif content.state == state.ACCELERATE:
          grid[x][y] = color_map[7]
  return grid

class Car:
    def __init__(self, actual_state, x, y, agent_id, speed):
        self.state = actual_state
        self.speed = speed
        self.position= [x,y]
        self.id = agent_id

# we only use x and z 
class car_agent(Agent):
  def __init__(self, unique_id, model, x, y):
    super().__init__(unique_id, model)
    # El auto inicia como detenido
    self.state = state.STOP
    self.speed = 0
    self.max_speed = 3
    self.waiting = 0
    # self.actual_car = Car(self.state, x, y, self.unique_id, self.speed)
  
  def step(self):    
    if self.pos[1]+1 == self.model.road_length:
      self.model.road_end(self)
      return self.generate_car_state()
    
    # CAR BREAKS
    chance = randrange(1000)
    # Contiguos cars cannot break and a car in the simulation will break after two minutes
    if chance == 0 and self.model.step_number > 40 and self.model.road_length / 3 < self.pos[1]:
      self.engine_fail()
      return self.generate_car_state()

    # Car is broken so we dont perform any other action
    if self.state == state.BREAK:
      if self.speed > 0:
        self.speed -= 1
        self.move()
      return self.generate_car_state()
    
    # TURNING
    # We check if the car is currently waiting in line and if it is at the front, we make it try to turn, else it waits
    if self.state == state.STOP and self.is_at_front():
      if self.can_move_sides():
        self.move_sides()
        self.speed = 0
        return self.generate_car_state()
    
    # MOVING
    if self.can_accelerate():
      self.accelerate()
      if self.speed == self.max_speed:
        self.state = state.ADVANCE
        return self.generate_car_state()
    elif self.has_to_decelerate():
      self.decelerate()
      if self.speed == 0:
        self.state = state.STOP
        return self.generate_car_state()
    
    if self.can_move():
      self.move()
      return self.generate_car_state()
    else:
      self.speed = 0
      self.state = state.STOP
      return self.generate_car_state()

  # GENERATE CAR STATE OBJECT
  def generate_car_state(self):
    # self.actual_car = Car(self.state,self.pos[0],self.pos[1],self.unique_id,self.speed)
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
      if self.can_move_side(self.pos[0] + 1):
        self.move_to_lane(self.pos[0] + 1)
        self.state = state.MOVE_LEFT
      elif self.can_move_side(self.pos[0] - 1):
        self.move_to_lane(self.pos[0] - 1)
        self.state = state.MOVE_RIGHT

  # MOVE CAR TO LANE
  def move_to_lane(self, lane):
    self.model.grid.move_agent(self, (lane, self.pos[1]))

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
    for i in range(0, self.calc_braking_distance(3)):
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
      self.model.road_end(self)
  
  # CAR FAILS - NO CAR CAN FAIL IF A NEARBY CAR HAS ALREADY FAILED
  def engine_fail(self):
    neighbors=self.model.grid.get_neighbors((self.pos[0], self.pos[1]),True, False,5)
    for agent in neighbors:
      if agent.state == state.BREAK:
        return
    print("ROTO", self.pos[0], "-", self.pos[1])
    self.state = state.BREAK

  # CHECK IF POSITION IS A VALID ROAD LOCATION
  def is_in_bounds(self, pos):
    return pos >= 0 and pos + 1 <= self.model.road_length

  # DECELERATE CAR
  def decelerate(self):
    self.state = state.DECELERATE
    self.speed -= 1

  # ACCELERATE CAR
  def accelerate(self):
    self.state = state.ACCELERATE
    self.speed += 1
    
class road_model(Model):
    def __init__(self, max_cars, road_length, number_road):
        self.number_cars = 0
        self.max_cars = max_cars
        self.road_length = road_length
        self.number_road = number_road
        self.car_id = 0
        self.grid = SingleGrid(self.number_road, self.road_length, False)
        self.schedule = SimultaneousActivation(self)
        self.step_number = 0;

        self.datacollector_graphic = DataCollector(model_reporters={"Grid": get_grid})
        self.datacollector_server = DataCollector(model_reporters={"Agents": get_grid_server})

  # when the car arrives to the end 
    def road_end(self, agent):
        self.schedule.remove(agent)
        self.grid.remove_agent(agent)

    def generate_new_car(self, road):
        a = car_agent(self.car_id, self, road, 0)
        # generate the car position
        self.grid.place_agent(a, (road, 0))
        self.schedule.add(a)
        self.car_id += 1

    def generate_new_cars(self):
        if self.number_cars < self.max_cars:
            for i in range(self.number_road):
                chance = randrange(3)
                if chance == 1 and self.number_cars < self.max_cars and self.grid.is_cell_empty((i, 0)):
                    self.generate_new_car(i)
                    self.number_cars += 1

    def step(self):
        """ Ejecuta un paso de la simulación."""
        self.step_number += 1
        self.schedule.step()
        self.generate_new_cars()
        self.datacollector_graphic.collect(self)
        self.datacollector_server.collect(self)
        
MAX_GENERATIONS = 200
max_cars = 100
number_road = 3
road_length = 100

model = road_model(max_cars, road_length, number_road)
i = 0

while i < MAX_GENERATIONS:
  model.step()
  i += 1