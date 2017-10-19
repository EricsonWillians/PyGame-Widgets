import pygame
from PyCliche import core

class Component:

	def __init__(self, pos, dimensions, parent):
		self.pos = pos
		self.dimensions = dimensions
		self.parent = parent
		self.parent_x_positions = [0]
		self.parent_y_positions = [0]
		
class Widget(Component):
	
	def __init__(self, pos, dimensions, parent=None):
		Component.__init__(self, pos, dimensions, parent)
		
class RectWidget(Widget):
	
	def __init__(self, pos, dimensions, parent=None):
		Component.__init__(self, pos, dimensions, parent)
		self.color = (0, 0, 0, 0)
		self.width = core.FILLED
		self.pos = pos
		self.dimensions = dimensions
		self.rect = None

	def set_color(self, rgba):
		self.color = rgba
		self.rect = core.Rectangle(self.color, self.pos, self.dimensions, self.width)

	def set_width(self, width):
		self.width = width
		self.rect = core.Rectangle(self.color, self.pos, self.dimensions, self.width)

	def set_solid(self, value):
		if value:
			self.set_width(0)
		else:
			self.set_width(core.DEFAULT_WIDTH)

	def set_span(self, span):
		self.span = [span[0]+1, span[1]+1]
		self.span_w = sum([self.dimensions[0] for w in range(self.span[0])])
		self.span_h = sum([self.dimensions[1] for h in range(self.span[1])])
		self.dimensions = [
			self.span_w,
			self.span_h
		]
		self.rect = core.Rectangle(self.color, self.pos, self.dimensions, self.width)
		if hasattr(self, "text"): self.set_text(self.text.value)

	def set_image(self, path):
		self.image = pygame.transform.scale(
			pygame.image.load(path), 
			(self.dimensions[0], self.dimensions[1])
		)

	def set_border(self, color, width):
		if width == 0: raise Exception("Border width cannot be 0.")
		border_dimensions = [
			self.dimensions[0] + (width * 2),
			self.dimensions[1] + (width * 2)
		]
		border_pos = [
			self.pos[0] - width,
			self.pos[1] - width
		]
		self.border = core.Rectangle(color, self.pos, self.dimensions, width)

	def draw_image(self, surface):
		surface.blit(self.image, (self.pos[0], self.pos[1]))

	def draw(self, surface):
		self.rect.draw(surface)
		if hasattr(self, "image"): self.draw_image(surface)
		if hasattr(self, "border"): self.border.draw(surface)

def rpc(p, l=[]):
	if p.parent:
		rpc(p.parent)
	else:
		l.append(p)
	return l

class Panel(RectWidget):
	
	def __init__(self, grid=None, parent=None, position_in_grid=None, pos=None):
		if pos:
			self.pos = pos
		else:
			self.pos = (0, 0)
		self.grid = grid
		self.dimensions = (
			self.grid.grid_size[0] * self.grid.cell_size[0], 
			self.grid.grid_size[1] * self.grid.cell_size[1]
		)
		self.x_positions = [x for x in range(0, self.dimensions[0], self.grid.cell_size[0])]
		self.y_positions = [x for x in range(0, self.dimensions[1], self.grid.cell_size[1])]
		if (parent and position_in_grid):
			self.parent = parent
			self.position_in_grid = position_in_grid
			parents = rpc(parent)
			lastParent = parents[len(parents)-1]
			self.x_positions = [x for x in range(0, lastParent.dimensions[0], lastParent.grid.cell_size[0])]
			self.y_positions = [x for x in range(0, lastParent.dimensions[1], lastParent.grid.cell_size[1])]
			self.dimensions = [
				lastParent.grid.cell_size[0], 
				lastParent.grid.cell_size[1]
			]
			self.pos = (
				self.x_positions[self.position_in_grid[0]] + lastParent.pos[0],
				self.y_positions[self.position_in_grid[1]] + lastParent.pos[1]
			)
		else:
			self.position_in_grid = (0, 0)
		RectWidget.__init__(self, self.pos, self.dimensions)
		self.rect = core.Rectangle(self.color, self.pos, self.dimensions, self.width)
		
class RectButton(RectWidget):

	def __init__(self, parent, position_in_grid):
		self.parent = parent
		self.position_in_grid = position_in_grid
		self.dimensions = [
			self.parent.grid.cell_size[0], 
			self.parent.grid.cell_size[1]
		]
		self.x_positions = [x for x in range(0, self.parent.dimensions[0], self.dimensions[0])]
		self.y_positions = [x for x in range(0, self.parent.dimensions[1], self.dimensions[1])]
		self.pos = [
			self.x_positions[self.position_in_grid[0]] + self.parent.pos[0],
			self.y_positions[self.position_in_grid[1]] + self.parent.pos[1]
		]
		RectWidget.__init__(self, self.pos, self.dimensions, self.parent)
		self.rect = core.Rectangle(self.color, self.pos, self.dimensions)

	def on_click(self, event, function, *args):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if self.rect.R.collidepoint(event.pos):
					function(*args) if args else function()

	def on_release(self, event, function, *args):
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				if self.rect.R.collidepoint(event.pos):
					function(*args) if args else function()

	def on_mouse_button_click(self, event, mouse_button, function, *args):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == mouse_button:
				if self.rect.R.collidepoint(event.pos):
					function(*args) if args else function()

	def on_mouse_button_release(self, event, mouse_button, function, *args):
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == mouse_button:
				if self.rect.R.collidepoint(event.pos):
					function(*args) if args else function()

class TextButton(RectButton):

	def __init__(self, parent, position_in_grid, text):
		RectButton.__init__(self, parent, position_in_grid)
		self.text = text
		self.set_text(text.value)
		
	def set_text(self, new_text):
		self.half_w = self.dimensions[0] / 2
		self.half_h = self.dimensions[1] / 2
		self.text_rect = self.text.font.render(
			self.text.value, 
			1, 
			self.text.color
		)
		self.half_text_w = self.text_rect.get_rect().width / 2
		self.half_text_h = self.text_rect.get_rect().height / 2
		self.text.value = new_text
		self.text_rect = self.text.font.render(
			self.text.value, 
			1, 
			self.text.color
		)

	def draw(self, surface):
		self.rect.draw(surface)
		if hasattr(self, "border"): self.border.draw(surface)
		if hasattr(self, "image"): self.draw_image(surface)
		surface.blit(
			self.text_rect, 
			(self.pos[0] + (self.half_w - self.half_text_w), self.pos[1] + (self.half_h - self.half_text_h), self.dimensions[0], self.dimensions[1])
		)

