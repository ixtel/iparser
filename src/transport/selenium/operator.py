from http.client import HTTPException
from random import randint

from itools.timer.tools import slp
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from urllib3.exceptions import HTTPError

from .config import log, CONF
from .coordinator import Coordinator
from .curve import MouseCurve
from .elementor import Elementor
from .injector import Injector
from .selector import Selector

__all__ = ('Operator',)

from .utils.helper import sizer


class Operator:
	def __init__(self, driver: WebDriver):
		self.Driver = driver
		self.Selector = Selector(self.Driver)
		self.MouseCurve = MouseCurve()
		self.Injector = Injector(self.Driver)
		self.Elementor = Elementor(self.Driver)
		self.Coordinator = Coordinator(self.Driver)
		pass
	
	def mouse_init(self, x, y):
		ActionChains(self.Driver).move_by_offset(x, y).perform()
		pass
	
	def cursor_rnd(self):
		_r = self.Coordinator.coordinates_get_random(fullsize=False)
		self.mouse_init(_r['x'], _r['y'])
		return _r
	
	def cursor(self):
		# проверка формы координат курсора и получение его координат
		try:
			form = self.Selector.select_one(selector='form[name="cursorShowCoordinates"]', wait=1)
		except Exception as ex:
			log('Exception form', ex, level='warning')
			form = None
		if form is None:
			self.Injector.cmd_inject('cursor_position')
			slp(0.5, 1.5)
			self.cursor_rnd()
		try:
			x = int(self.Selector.select_one(selector='input#MouseX', attr_name='value', wait=1))
			y = int(self.Selector.select_one(selector='input#MouseY', attr_name='value', wait=1))
		except Exception as ex:
			log('Exception find ("MouseXY")', ex, level='warning')
			x = 0
			y = 0
		if x is None or y is None:
			x = 0
			y = 0
		cur = dict(
			x=x,
			y=y
		)
		return cur
	
	def cursor_to_place(self, place):
		coordinates = self.cursor()
		try:
			((left, right), (top, bottom)) = place
			
			to_up = coordinates['y'] - bottom + 1
			to_down = top - coordinates['y'] + 1
			to_left = coordinates['x'] - right + 1
			to_right = left - coordinates['x'] + 1
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log('Exception', ex, level='warning')
			raise ex
		if to_left > 0:
			x = -1 * to_left
		elif to_right > 0:
			x = to_right
		else:
			x = 0
		
		if to_up > 0:
			y = -1 * to_up
		elif to_down > 0:
			y = to_down
		else:
			y = 0
		
		return x, y
	
	def cursor_to_workplace(self):
		return self.cursor_to_place(self.Coordinator.current_workplace())
	
	def cursor_check_in_element(self, elm):
		place = self.Coordinator.place_under_element(elm, dx=-30, dy=-30)
		return self.cursor_check_to_place(place)
	
	def cursor_in_workplace(self):
		return self.Coordinator.coordinates_check_workplace(self.cursor())
	
	def cursor_in_place(self, place, width=0, height=0):
		try:
			return self.Coordinator.coordinates_check_in_place(coordinates=self.cursor(), place=place, width=width, height=height)
		except Exception as ex:
			log('Exception coordinates', ex, level='warning')
			raise ex
	
	def cursor_check_to_place(self, place):
		for i in range(3):
			if self.cursor_in_place(place):
				return True
			x, y = self.cursor_to_place(place)
			log(f'cursor {self.cursor()} NOT in place {place} offset place, {x}, {y}')
			self.mouse_move_by_offset(x, y)
		return False
	
	def cursor_check_to_workplace(self):
		return self.cursor_check_to_place(self.Coordinator.current_workplace())
	
	def click_inplace(self):
		try:
			ActionChains(self.Driver).click().perform()
			return True
		except Exception as ex:
			log('Warning', ex)
			self.Elementor.press_esc()
			return False
	
	def click_on_place_element(self, elm):
		self.cursor_check_in_element(elm)
		self.click_inplace()
		return True
	
	def click_on_element(self, elm):
		# TODO не кликать на ютуб и пр. внешние сайты
		if CONF.BROWSER == 'phantom':
			try:
				self.Elementor.element_click_js(elm)
				return True
			except Exception as ex:
				log('Exception phantom', ex, level='warning')
				return False
		else:
			try:
				ActionChains(self.Driver).click(elm).perform()
				return True
			except (HTTPError, HTTPException) as ex:
				log('Exception HTTP', ex, level='warning')
				raise ex
			except ElementClickInterceptedException as ex:
				log(f'Exception ElementClickInterceptedException', ex, elm, level='info')
				return False
			except WebDriverException as ex:
				log(f'Exception WebDriverException', ex, elm, level='info')
				return False
			except Exception as ex:
				log('Exception', ex, level='warning')
				return False
	
	def element_on_cursor(self):
		_e = self.Coordinator.element_on_coordinates(self.cursor()['x'], self.cursor()['y'])
		return _e
	
	def mouse_move_by_offset(self, x, y, sleep=0.5):
		try:
			ActionChains(self.Driver).move_by_offset(x, y).perform()
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log('Exception', ex, level='warning')
			return None
		slp(sleep)
	
	def mouse_teleport_to_element(self, elm):
		size = sizer(elm.size)
		
		try:
			ActionChains(self.Driver).move_to_element_with_offset(elm, randint(1, size['x']), randint(1, size['y'])).perform()
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log('Exception', ex, level='warning')
			return None
		slp(0, 0.5)
	
	def mouse_move_by_track(self, track, sleep=0.0):
		for step in track:
			if self.cursor_check_to_workplace() is False:
				log('MOVE not in workplace', level='warning')
				break
			self.mouse_move_by_offset(step['x'], step['y'], sleep)
	
	def mouse_move_to_place(self, place=None):
		if place is None:
			place = self.Coordinator.current_workplace()
		# TODO проверить сдвиг окна
		try:
			curve = self.Coordinator.pointcurve_to_place(self.cursor(), place)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			raise ex
		try:
			self.mouse_move_by_track(curve)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			raise ex
		pass
	
	def element_wait_press_enter(self, selector):
		elm = self.Selector.select_one(selector=selector)
		self.Elementor.element_press_enter(elm)
		return elm
	
	def scroll(self, x=None, y=None):
		"""
		скрол рабочего окна на х вправо и y вниз от нуля(левого верхнего края)
		:param x:
		:param y:
		:return:
		"""
		x = x if x is not None else self.Coordinator.left()  # если не указано смещение сохранять левый край на месте
		y = y if y is not None else self.Coordinator.top()  # если не указано смещение сохранять верхний край на месте
		return self.Injector.cmd_inject('scroll', script_args=(x, y))
	
	def scroll_offset(self, offset_x=0, offset_y=0):
		x = self.Coordinator.left() + offset_x  # создание абсолютной координаты
		y = self.Coordinator.top() + offset_y  # для javacript инъекции
		return self.scroll(x, y)
	
	def scroll_page(self, offset_x=0, offset_y=0):
		self.cursor_check_to_workplace()
		_down_line = self.Coordinator.downline()
		self.scroll_offset(offset_x, offset_y)
		if self.Coordinator.downline() == _down_line:
			log('Exception scroll not work', level='warning')
		else:
			self.mouse_move_by_offset(offset_x, offset_y)
	
	def stop_load_page(self):
		return self.Injector.cmd_inject('stop_load')
	
	def page_clear(self):
		try:
			self.Elementor.elements_click_jscss()
			self.Elementor.elements_remove()
			
			self.Injector.helper()
			self.Injector.jqury()
			self.Injector.xpather()
			self.Injector.mouse_trail()
			self.cursor()
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			raise ex
	
	def element_on_cursor_equal_selector(self, selestor):
		elm = self.element_on_cursor()
		try:
			trig = self.Elementor.selector_on_element(elm) == selestor
			return trig
		except Exception as ex:
			log('Warning elm_cur, e_target', ex, elm, selestor)
			return False
