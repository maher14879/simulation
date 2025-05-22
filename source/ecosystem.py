import numpy as np
from source.graphics import Graphics

WORLD_SIZE = 1000
FOOD_VARIANCE = 400
CELL_DISTANCE = 13
EAT_DISTANCE = 8
FOOD_VALUE = 1
START_ENERGY = 100
HUNGER_PER_CELL = 0.001

class Vision():
	def __init__(self, fov: float, food: float, cell: float):
		radius = 100
		self.fov = fov
		self.radius = radius
		self.cos_half_angle = np.cos(fov / 2)
		self.radius_squared = radius**2
		self.food = food
		self.cells = cell

	def get_seen(self, direction: np.ndarray, position: np.ndarray, positions: np.ndarray) -> np.ndarray:
		vectors = positions - position
		vectors = vectors[~(vectors == 0).all(axis=1)]
		distances_squared = np.sum(vectors**2, axis=1)
		vectors = vectors[distances_squared <= self.radius_squared]
		if not vectors.size > 0: return np.array([0., 0.])
		norms = np.linalg.norm(vectors, axis=1, keepdims=True)
		normalized_vectors = vectors / norms
		cos_angles = np.sum(normalized_vectors * direction, axis=1)
		normalized_vectors = normalized_vectors[cos_angles >= self.cos_half_angle]
		if normalized_vectors.size == 0: return np.array([0., 0.])
		average_direction = np.mean(normalized_vectors, axis=0)
		return average_direction
	
	def get_signal(self, direction: np.ndarray, position: np.ndarray, cell_positions: np.ndarray, food_positions: np.ndarray):
		signal = np.array([0., 0.])
		signal += self.get_seen(direction, position, cell_positions) * self.cells
		signal += self.get_seen(direction, position, food_positions) * self.food
		return signal

class Cell():
	def __init__(self, position: np.ndarray, direction: np.ndarray, dna: dict):
		self.position = np.array(position, dtype=float)
		self.direction = np.array(direction, dtype=float)
		self.dna = dna

		self.type = dna["type"]
		self.vision = Vision(dna["vision"]["fov"], dna["vision"]["food"], dna["vision"]["cell"]) if self.type == "vision" else None
	
	def metabolize(self, cell_positions: np.ndarray, food_positions: np.ndarray, signal: np.ndarray, direction: np.ndarray):
		if self.type == "vision": 
			signal = self.vision.get_signal(self.direction.copy(), self.position.copy(), cell_positions, food_positions)
		
		if self.type == "motor":
			direction += signal

		return signal, direction

class Creature():
	def __init__(self, position: np.ndarray, direction: np.ndarray, dna: list[dict] = []):
		self.position = np.array(position, dtype=float)
		self.direction = np.array(direction, dtype=float)
		self.dna = dna

		self.cells: list[Cell] = []
		for cell_dna in dna:
			cell = Cell(self.position, self.direction, cell_dna)
			self.cells.append(cell)

		self.energy = START_ENERGY
		self.hunger = len(self.cells) * HUNGER_PER_CELL

	def metabolize(self, cell_positions: np.ndarray, food_positions: np.ndarray):
		signal = np.array([0., 0.])
		direction = np.array([0., 0.])

		for cell in self.cells: signal, direction = cell.metabolize(cell_positions, food_positions, signal, direction)
		
		self.direction = direction
		self.position = self.position + self.direction
		self.energy -= self.hunger

		last_position = self.position
		for i, cell in enumerate(self.cells):
			cell_direction = last_position - cell.position
			distance = np.linalg.norm(cell_direction)
			if distance > CELL_DISTANCE:
				normalized_direction = cell_direction / distance
				self.cells[i].position += normalized_direction * (distance - CELL_DISTANCE)
				self.cells[i].direction = normalized_direction

			last_position = cell.position

	def eat_food(self, food_positions: np.ndarray): 
		vectors = food_positions - self.position
		square_distances = np.sum(vectors**2, axis=1)
		self.energy += np.sum(square_distances <= EAT_DISTANCE**2) * FOOD_VALUE
		return food_positions[square_distances > EAT_DISTANCE**2]

	def clone(self) -> "Creature":
		pass
	
class Ecosystem():
	def __init__(self, creatures: list[Creature] = [], food: np.ndarray[float] = np.empty((0, 2)), spawn_food: float = 1, max_food: float = 100):
		self.creatures = creatures
		self.food = np.array(food)
		self.spawn_food = spawn_food
		self.max_food = max_food
		self.spawn_food_count = 0
		self.time = 0
		self.tick_count = 0
		self.graphics = Graphics()
		self.graphics.setup()

	def tick(self):
			self.tick_count += 1
			self.spawn_food_count += 1

			if self.spawn_food_count > self.spawn_food:
				if self.food.size <= self.max_food: self.food = np.vstack([self.food, np.random.normal(0, FOOD_VARIANCE, size=2)])
				self.spawn_food_count = 0

			cell_positions = []
			for creature in self.creatures: cell_positions += [cell.position for cell in creature.cells]

			food_positions = np.copy(self.food)

			for creature in self.creatures:
				if self.food.size > 0: self.food = creature.eat_food(food_positions)
				creature.metabolize(cell_positions, food_positions)
				if creature.energy < 0:
					self.creatures.remove(creature)
					continue
	
	def draw(self, dt: float, center: np.ndarray):
		cell_list = []
		for creature in self.creatures: 
			cell_list += [(cell.type, cell.position) for cell in creature.cells]
		
		print(cell_list)
		food_list = [("food", position) for position in self.food] if self.food.size > 0 else []
		self.graphics.update(dt, center, cell_list + food_list, self.tick_count)