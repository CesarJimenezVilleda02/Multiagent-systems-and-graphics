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

import final_car_agent, states, final_data_collector

class Road_model(Model):
  def __init__(self, road_length, number_road):
    self.road_length = road_length
    self.number_road = number_road
    self.car_id = 0
    self.grid = SingleGrid(self.number_road, self.road_length, False)
    self.schedule = SimultaneousActivation(self)
    self.step_number = 0;
    self.to_remove = []
    self.max_speeds = []
    self.finished_cars=0
    self.total_moves=0
    self.total_stops=0
    self.speeds = np.zeros((self.number_road,self.road_length))

    self.datacollector_graphic = DataCollector(model_reporters={"Grid": final_data_collector.get_grid})
    self.datacollector_server = DataCollector(model_reporters={"Agents": final_data_collector.get_grid_server})

    # Initialize lane max speeds
    for i in range(self.number_road):
      self.max_speeds.append(self.number_road - i)
      for j in range(self.road_length):
        self.speeds[i][j] = self.number_road - i

  def remove_cars(self):
    for i in range(len(self.to_remove)):
      agent = self.to_remove[i]
      self.grid.remove_agent(agent)
      self.schedule.remove(agent)
    self.to_remove = []

  def generate_new_car(self, road):
      a = final_car_agent.Car_agent(self.car_id, self)
      # generate the car position
      self.grid.place_agent(a, (road, 0))
      self.schedule.add(a)
      self.car_id += 1

  def generate_new_cars(self):
      for i in range(self.number_road):
        chance = randrange(5)
        if chance == 1 and self.grid.is_cell_empty((i, 0)):
          self.generate_new_car(i)

  def step(self):
    """ Ejecuta un paso de la simulación."""
    self.datacollector_graphic.collect(self)
    self.datacollector_server.collect(self)
    self.step_number += 1
    self.schedule.step()
    self.remove_cars()
    self.generate_new_cars()