from __future__ import division
import pyglet
pyglet.options['shadow_window'] = False
pyglet.options['debug_gl'] = False
from pyglet import gl
from struct import unpack
import threading
import os, math, time

background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
overlay = pyglet.graphics.OrderedGroup(2)

mainApp = None

def get_pixel(image, x, y):
	rawimage = image.get_image_data()
	format = 'RGBA'
	pitch = rawimage.width * len(format)
	pixels = rawimage.get_data(format, pitch)
	data = unpack("%iB" % (len(format) * rawimage.width * rawimage.height), pixels)
	index = x * len(format) + y * pitch
	return data[index : (index + len(format))]

class Entity(object):
	
	_scale = 1
	_speed = 40
	
	def __init__(self, image, group=foreground, draggable=True):
		self.group = group
		image.anchor_x = image.width / 2
		image.anchor_y = image.height / 2
		self.sprite = pyglet.sprite.Sprite(image, group=self.group)
		self.draggable = draggable
		self.move_to_scaled(0, 0)
	
	def scale(self, scale):
		self.sprite.x *= scale / self._scale
		self.sprite.y *= scale / self._scale
		self.sprite.scale = scale
		self._scale = scale
	
	def check_pos(self, x, y):
		tmpx = x - self.sprite.x
		tmpy = y - self.sprite.y
		if abs(tmpx) < self.sprite.width / 2 and abs(tmpy) < self.sprite.height / 2:
			x = tmpx * math.cos(math.radians(self.sprite.rotation)) - tmpy * math.sin(math.radians(self.sprite.rotation)) + self.sprite.width / 2
			y = tmpx * math.sin(math.radians(self.sprite.rotation)) + tmpy * math.cos(math.radians(self.sprite.rotation)) + self.sprite.height / 2
			ix = int(x / self.sprite.scale)
			iy = int(y / self.sprite.scale)
			data = get_pixel(self.sprite.image, ix, iy)
			return data[3] > 0
		return False
	
	def move(self, x, y):
		self.sprite.x += x
		self.sprite.y += y
	
	def move_to(self, x, y):
		self.sprite.x = x
		self.sprite.y = y
	
	def move_scaled(self, x, y):
		self.sprite.x += x * self._scale
		self.sprite.y += y * self._scale
	
	def move_to_scaled(self, x, y):
		global mainApp
		self.sprite.x = (x + mainApp.size[0] / 2) * self._scale
		self.sprite.y = (y + mainApp.size[1] / 2) * self._scale
	
	def set_group(self, group=None):
		if group:
			self.sprite.group = group
		else:
			self.sprite.group = self.group
	
	def forward(self, len):
		self.sprite.x += len * math.cos(math.radians(self.sprite.rotation))
		self.sprite.y += len * math.sin(-math.radians(self.sprite.rotation))
		time.sleep(1/self._speed) # animation
	
	def turnRight(self, degrees):
		self.sprite.rotation += degrees
		time.sleep(1/self._speed) # animation
	
	def turnLeft(self, degrees):
		self.sprite.rotation -= degrees
		time.sleep(1/self._speed) # animation
	
	def gotoXY(self, x, y):
		self.move_to_scaled(x, y)
		time.sleep(1/self._speed) # animation
	
	def doGlide(self, seconds, x, y):
		steps = seconds * self._speed
		diffX = (x + mainApp.size[0] / 2 - self.sprite.x) / steps
		diffY = (y + mainApp.size[1] / 2 - self.sprite.y) / steps
		for i in range(int(steps)):
			self.move_scaled(diffX, diffY)
			time.sleep(1/self._speed) # animation
		self.move_to_scaled(x, y)
	
	def receiveGO(self):
		pass

class App(object):

	_scale = 1

	def __init__(self, create_window=True):
		if create_window:
			self.window = pyglet.window.Window(resizable=True)
			dispatcher = self.window
		else:
			pyglet.resource.path = [os.getcwd() + '/python']
			pyglet.resource.reindex()
			context = FakeContext()
			context.set_current()
			dispatcher = widget
			self.window = None
		
		dispatcher.push_handlers(
			on_draw=self.on_draw,
			on_resize=self.on_resize,
			on_mouse_press=self.on_mouse_press,
			on_mouse_release=self.on_mouse_release,
			on_mouse_drag=self.on_mouse_drag,
		)
		
		self.batch = pyglet.graphics.Batch()
		
		self.size = (480, 360)
		self.dragging = None
		
		self.entities = []
	
	def add_entity(self, entity):
		entity.sprite.batch = self.batch
		entity.scale(self._scale)
		self.entities.append(entity)
	
	def reset(self):
		del self.entities[:]
	
	def on_draw(self):
		if self.window:
			self.window.clear()
		self.batch.draw()
	
	def on_resize(self, width, height):
		self._scale = min(width / self.size[0], height / self.size[1])
		for entity in self.entities:
			entity.scale(self._scale)

	def on_mouse_press(self, x, y, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT:
			for entity in self.entities:
				if entity.draggable and entity.check_pos(x, y):
					self.dragging = entity
					self.dragging.set_group(overlay)
					break
	
	def on_mouse_release(self, x, y, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT and self.dragging:
			self.dragging.set_group()
			self.dragging = None
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT and self.dragging:
			self.dragging.move(dx, dy)

	def on_start(self):
		for entity in self.entities:
			t = threading.Thread(target=entity.receiveGO)
			t.start()

class FakeContext(gl.Context):
	def __init__(self, config=None, context_share=None):
		self.config = config
		self.context_share = context_share
		self.canvas = None
		if context_share:
			self.object_space = context_share.object_space
		else:
			self.object_space = gl.ObjectSpace()
	
	def attach(self, canvas=None):
		pass
	
	def detach(self):
		pass
	
	def set_current(self):
		# XXX not per-thread
		gl.current_context = self
		# XXX
		gl.gl_info.set_active_context()
		gl.glu_info.set_active_context()
		# Implement workarounds
		if not self._info:
			self._info = gl.gl_info.GLInfo()
			self._info.set_active_context()
			for attr, check in self._workaround_checks:
				setattr(self, attr, check(self._info))
		# Release textures and buffers on this context scheduled for deletion.
		# Note that the garbage collector may introduce a race condition,
		# so operate on a copy of the textures/buffers and remove the deleted
		# items using list slicing (which is an atomic operation)
		if self.object_space._doomed_textures:
			textures = self.object_space._doomed_textures[:]
			textures = (gl.GLuint * len(textures))(*textures)
			gl.glDeleteTextures(len(textures), textures)
			self.object_space._doomed_textures[0:len(textures)] = []
		if self.object_space._doomed_buffers:
			buffers = self.object_space._doomed_buffers[:]
			buffers = (gl.GLuint * len(buffers))(*buffers)
			gl.glDeleteBuffers(len(buffers), buffers)
			self.object_space._doomed_buffers[0:len(buffers)] = []

class Widget(pyglet.event.EventDispatcher):
	def on_resize(self, width, height):
		gl.glViewport(0, 0, width, height)
		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glLoadIdentity()
		gl.glOrtho(0, width, 0, height, -1, 1)
		gl.glMatrixMode(gl.GL_MODELVIEW)

widget = Widget()

def draw():
	widget.dispatch_event('on_draw')

def resize(width, height):
	widget.dispatch_event('on_resize', width, height)

def mouse_press(x, y, buttons, modifiers):
	widget.dispatch_event('on_mouse_press', x, y, pyglet.window.mouse.LEFT, modifiers)

def mouse_release(x, y, buttons, modifiers):
	widget.dispatch_event('on_mouse_release', x, y, pyglet.window.mouse.LEFT, modifiers)

def mouse_drag(x, y, dx, dy, buttons, modifiers):
	widget.dispatch_event('on_mouse_drag', x, y, dx, dy, pyglet.window.mouse.LEFT, modifiers)
	
def start():
	global mainApp
	if mainApp:
		mainApp.on_start()

def init(background_file, create_window=True):
	global mainApp
	if mainApp:
		mainApp.reset()
	else:
		mainApp = App(create_window=create_window)
	mainApp.add_entity(Entity(pyglet.resource.image(background_file), background, draggable=False))  # TODO: store this
	return mainApp

Widget.register_event_type('on_draw')
Widget.register_event_type('on_resize')
Widget.register_event_type('on_mouse_press')
Widget.register_event_type('on_mouse_release')
Widget.register_event_type('on_mouse_drag')
