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

import final_car_agent, final_model
from states import state

def get_grid_server(model):
  agents = []
  for agent in model.schedule.agents:
    agent_obj = {
      "id": agent.unique_id, 
      "state": agent.state.name, 
      "speed": agent.speed, 
      "x": agent.pos[1], 
      "z": agent.pos[0]
    }
    agents.append(agent_obj)
  return agents

def get_grid(model):
  # define color map 
  color_map = {1: np.array([220, 220, 220]), # road
              2: np.array([255, 51, 51]), # red
              3: np.array([128, 255, 0]), # green
              4: np.array([255, 128, 0]), # orange
              5: np.array([0, 0, 0]), # broken
              6: np.array([255, 255, 0]), # decelerate
              7: np.array([153, 204, 255]), # accelerate 
              8: np.array([128, 0, 0])} # eliminate 

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
        elif content.state == state.ELIMINATE:
          grid[x][y] = color_map[8]
        elif content.state == state.SPAWN:
          grid[x][y] = color_map[8]
  return grid