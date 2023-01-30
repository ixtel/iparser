from http.client import HTTPException
from random import randint

from selenium.webdriver import Remote as WebDriver
from urllib3.exceptions import HTTPError

from .config import log
from .curve import MouseCurve
from .injector import Injector
from .selector import Selector

__all__ = ('Coordinator',)

from .utils.helper import sizer


def randint_with_revers(start, end):
	return randint(min(start, end), max(start, end))


class Coordinator:
	def __init__(self, driver: WebDriver):
		self.Driver = driver
		self.Injector = Injector(driver=driver)
		self.Selector = Selector(driver=driver)
		self.MouseCurve = MouseCurve()
		pass
	
	def bottom(self):
		"""
		высота страницы ниже текущего окна
		:return: int = self.body_height() - self.workplace()['height'] - self.top()
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('bottom')
	
	def right(self):
		"""
		длинна страницы правее текущего окна
		:return: int = self.body_width() - self.workplace()['width'] - self.left()
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('right')
	
	def downline(self):
		"""
		y координата нижнего края текущего окна
		:return: int = self.workplace()['height'] + self.top()
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('downline')
	
	def rightline(self):
		"""
		x координата правого края текущего окна
				:return: int = self.workplace()['width'] + self.left()
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('rightline')
	
	def resolute(self):
		"""
		разрешение экрана(размер монитора)
		:return: dict = {width: int, height: int}
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('resolute')
	
	def window_size(self):
		"""
		размер окна браузера
		
		:return: dict = {width: int, height: int}
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('window_size')
	
	def body_height(self):
		"""
		высота страницы сайта
		:return: int
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('body_height')
	
	def body_width(self):
		"""
		ширина страницы сайта
		:return: int
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('body_width')
	
	def top(self):
		"""
		координата(смешение рабочего окна от верха страницы)
		:return: int
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('top')
	
	def left(self):
		"""
		координата(смешение рабочего окна от левого края страницы)
		:return: int
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('left')
	
	def workplace(self):
		"""
		размер рабочего пространство где отображается сайт
		:return: dict = {width: int, height: int}
		"""
		self.Injector.helper()
		return self.Injector.cmd_inject('workplace')
	
	def current_workplace(self):
		self.Injector.helper()
		try:
			return self.Injector.cmd_inject('current_workplace')
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			return (0, 0), (0, 0)
	
	def place_under_coordinates(self, coordinates, size=None, dx=0, dy=0, percent=True, workplace_padding=7):
		if size is None:
			size = {'x': 0, 'y': 0}
		if percent:
			dx = (size['x'] / 100) * dx
			dy = (size['y'] / 100) * dy
		
		left = coordinates['x'] - dx
		right = coordinates['x'] + size['x'] + dx
		top = coordinates['y'] - dy
		bottom = coordinates['y'] + size['y'] + dy
		
		try:
			left = max(left, self.left() + workplace_padding)
			right = min(right, self.rightline() - workplace_padding)
			top = max(top, self.top() + workplace_padding)
			bottom = min(bottom, self.downline() - workplace_padding)
			
			place = ((int(left), int(right)), (int(top), int(bottom)))
			return place
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			raise ex
	
	def place_under_element(self, elm, dx=0, dy=0, percent=True, workplace_padding=7):
		try:
			return self.place_under_coordinates(
				coordinates=elm.location, size=sizer(elm.size), dx=dx, dy=dy, percent=percent, workplace_padding=workplace_padding
			)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			raise ex
	
	@staticmethod
	def coordinates_check_in_place(coordinates, place, width=0, height=0):
		try:
			((left, right), (top, bottom)) = place
			notop = coordinates['y'] >= top
			nodown = coordinates['y'] + height <= bottom
			noleft = coordinates['x'] >= left
			noright = coordinates['x'] + width <= right
		except Exception as ex:
			log('Exception coordinates', ex, level='warning')
			raise ex
		return notop and nodown and noleft and noright
	
	def coordinates_get_random(self, fullsize=False, workplace_padding=7):
		(current_x, current_y) = self.current_workplace()
		try:
			x = randint(workplace_padding, int(self.body_width()) - workplace_padding) if fullsize else randint(*current_x)
			y = randint(workplace_padding, int(self.body_height()) - workplace_padding) if fullsize else randint(*current_y)
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log(f'Exception current_workplace={current_x, current_y}', ex, level='warning')
			x = 0
			y = 0
		point = dict(
			x=x,
			y=y
		)
		return point
	
	@staticmethod
	def avalible_check_element(elm):
		if elm is None:
			raise Exception('element is None')
		try:
			if elm.location['x'] < 0:
				return False
			if elm.location['y'] < 0:
				return False
			return True
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log('Exception', ex, level='warning')
			return None
	
	def workplace_check_element(self, elm):
		if elm is None:
			raise Exception('element is None')
		try:
			coordinates = {
				'x': elm.location['x'],
				'y': elm.location['y']
			}
			return self.coordinates_check_workplace(coordinates, elm.size['width'], elm.size['height'])
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log('Exception', ex, level='warning')
			return None
	
	def coordinates_check_workplace(self, coordinates, width=0, height=0):
		try:
			return self.coordinates_check_in_place(coordinates=coordinates, place=self.current_workplace(), width=width, height=height)
		except Exception as ex:
			log('Exception', ex, level='warning')
			raise ex
	
	def element_on_coordinates(self, x, y):
		path = self.Injector.selector_on_point({'x': x, 'y': y})
		return self.Selector.select_one(selector=path, wait=1)
	
	def pointcurve_to_place(self, start, place):
		# TODO -> coordinator.track_to_place
		end = self.get_coordinates_in_place(place)
		return self.MouseCurve.track_from_2point(
			start, end, self.current_workplace()
		)
	
	@staticmethod
	def get_coordinates_in_place(place):
		((left, right), (top, bottom)) = place
		x = randint_with_revers(left, right)
		y = randint_with_revers(top, bottom)
		end = {
			'x': x,
			'y': y
		}
		return end
