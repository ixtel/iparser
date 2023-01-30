import time
from collections import defaultdict
from http.client import HTTPException
from random import shuffle, choice, randint, uniform
import jsonpickle
from itools.dataminer.imath import random_triger_with_desp, chunk_count_to_list
from itools.network.tools import get_domain_from_url
from itexter.tools import keyboard_change
from itools.timer.tools import slp
from itools.rewr.tools import str_filter_by_list
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, JavascriptException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from urllib3.exceptions import HTTPError
from selenium.webdriver.support.ui import Select

from .browser import Browser
from .config import log
from .constants.navigator import STOP_HREF
from .coordinator import Coordinator
from .curve import MouseCurve
from .elementor import Elementor
from .injector import Injector
from .operator import Operator
from .selector import Selector
from .utils.helper import random_chunk_distance, sizer, clean_url

__all__ = ('Navigator',)


class NavigatorBase(Browser):
	def __init__(
			self,
			driver: WebDriver,
			*args, **kwargs
	):
		super().__init__(driver, *args, **kwargs)
		self.Driver = driver
		self.MouseCurve = MouseCurve()
		self.Selector = Selector(self.Driver)
		self.Injector = Injector(self.Driver)
		self.Elementor = Elementor(self.Driver)
		self.Coordinator = Coordinator(self.Driver)
		self.Operator = Operator(self.Driver)
		
		self._trying_current_url = 0
		self._time_finit = 0
		self._action_history = defaultdict(list)
		self._tabs_handles = []
		self._tabs_url = []
	
	def init(self):
		self.Operator.page_clear()
	
	def timer_set(self, time_on_site):
		self._time_finit = int(time.time()) + int(time_on_site)
	
	def timer_get(self):
		if self._time_finit == 0:
			return True
		if int(time.time()) >= self._time_finit:
			self._time_finit = 0
			return False
		return True
	
	def get_cookies_object(self):
		return self.Driver.get_cookies()
	
	def get_cookies(self):
		cookies = self.Driver.get_cookies()
		return jsonpickle.encode(cookies)
	
	def current_url_check(self, target_url):
		try:
			if self.current_url().find(target_url) > -1:
				return True
		except Exception as ex:
			log(f'Exception target_url={target_url}', ex, level='warning')
		return False
	
	def current_url(self):
		try:
			self._trying_current_url += 1
		except Exception as _ex:
			log('Exception trying_current_url', _ex, level='warning')
			self._trying_current_url = 0
		try:
			_curl = self.Driver.current_url
			self._trying_current_url = 0
			return _curl
		except Exception as ex:
			log('Exception current_url', ex, level='warning')
			self.Operator.stop_load_page()
			if self._trying_current_url < 3:
				self._trying_current_url += 1
				return self.current_url()
			else:
				return ''
	
	def get_element(self, selector=None, parent=None, *args, **kwargs):
		return self.Selector.select_one(obj=parent, selector=selector, *args, **kwargs)
	
	def get_elements(self, selector=None, parent=None, *args, **kwargs):
		return self.Selector.select(obj=parent, selector=selector, *args, **kwargs)
	
	def site_open(self, url: str):
		if not url.startswith('http'):
			url = f'https://{url}'
		
		page = None
		try:
			page = self.Driver.get(url)
		except Exception as ex:
			log('Exception', ex, level='warning')
			self.Elementor.press_esc()
		slp(2, 4)
		log(f'page={page}, current_url={self.current_url()}')
		
		self.Operator.page_clear()
		
		body = None
		try:
			body = self.get_element('body')
		except Exception as ex:
			log('Exception', ex, level='warning')
			self.Elementor.press_esc()
		log(f'body={body}')
		
		slp(2, 4)
		
		return body
	
	def site_check(self, url):
		if self.current_url_check(url):
			log(f'url {url} in current_url {self.current_url()}')
			return True
		log(f'url {url} NOT in current_url {self.current_url()}')
		self.site_open(url)
		if self.current_url_check(url):
			log(f'url {url} in current_url {self.current_url()}')
			return True
		log(f'url {url} NOT in current_url {self.current_url()}')
		return False
	
	def add_history(self, action):
		self._action_history[self.current_url].append(action)
	
	def check_history(self):
		return len(self._action_history[self.current_url]) > 0


class NavigatorTabs(NavigatorBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._tab_handlers_saved = {}
	
	def tab_save_handler(self, name):
		self._tab_handlers_saved[name] = self.Driver.current_window_handle
	
	def tab_switch_to_handler(self, name):
		tab = self._tab_handlers_saved.get(name)
		try:
			self.Driver.switch_to.window(tab)
		except Exception as ex:
			log(f'Exception', name, ex, level='warning')
	
	def tab_check(self, url: str):
		# TODO refactoring
		slp(2, 4)
		for _ in self.tabs_switch():
			if self.current_url_check(url):
				log(f'url {url} in current_url {self.current_url()}')
				continue
			log(f'url {url} NOT in current_url {self.current_url()}')
			self.Operator.stop_load_page()
			self.tab_close()
		return self.site_check(url)
	
	def tabs_switch(self):
		try:
			tabs = self.Driver.window_handles
			for tab in tabs:
				try:
					self.Driver.switch_to.window(tab)
				except Exception as _ex:
					continue
				yield tab
		except Exception as _ex:
			yield None
	
	def tabs_urls(self):
		urls = []
		for _ in self.tabs_switch():
			url = self.current_url()
			urls.append(url)
		return urls
	
	def tab_close(self):
		self.Driver.close()
	
	def tabs_close_except(self, except_urls):
		if not except_urls:
			log('Exception not except_urls', level='warning')
			return None
		if not isinstance(except_urls, list):
			except_urls = [except_urls]
		for _ in self.tabs_switch():
			_curl = self.current_url()
			if str_filter_by_list(_curl, except_urls) is False:
				self.Operator.stop_load_page()
				slp(4, 8)
				self.tab_close()
			else:
				self.Operator.stop_load_page()
	
	def tabs_close_except_target(self, target_url):
		while len(self.Driver.window_handles) > 1:
			self.tabs_close_except(target_url)
			slp(1, 3)
	
	def tab_get_target(self, target_url):
		if not target_url:
			log('Exception not target_url', level='warning')
			return False
		if self.current_url_check(target_url):
			self.Operator.page_clear()
			return True
		for _ in self.tabs_switch():
			if self.current_url_check(target_url):
				self.Operator.page_clear()
				return True
		return False
	
	def tab_check_target(self, target_url=None):
		if target_url is None:
			log('Exception not target_url', level='warning')
			return False
		_current_handle = self.Driver.current_window_handle
		if self.current_url_check(target_url):
			return True
		result = False
		for _ in self.tabs_switch():
			if self.current_url_check(target_url):
				self.Operator.page_clear()
				result = True
				break
		try:
			self.Driver.switch_to.window(_current_handle)
		except Exception as ex:
			log("don't can switch to main tab", ex)
		return result
	
	def tabs_memory_url(self):
		self._tabs_url = self.tabs_urls()
	
	def tabs_compare_url(self):
		tabs_urls = self.tabs_urls()
		result = set(tabs_urls) - set(self._tabs_url)
		return result
	
	def tabs_memory_handles(self):
		self._tabs_handles = self.Driver.window_handles
		pass
	
	def tabs_compare_handles(self):
		result = set(self.Driver.window_handles) - set(self._tabs_handles)
		return result


class NavigatorHelper(NavigatorTabs):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
	def links_in_page(self, count=None, filtred=False):
		# TODO: рефакторинг. кликать и по картинкам и по относительным ссылкам
		elms = self.get_elements('a')
		links = []
		if elms is not None:
			for link in elms:
				if link.is_enabled() and link.is_displayed() and link.text:
					href = link.get_attribute('href')
					if href:
						if filtred:
							if str_filter_by_list(href, STOP_HREF) is False:
								links.append(link)
						else:
							links.append(link)
		if count:
			shuffle(links)
			_links = []
			for i in range(min(count, len(links))):
				_links.append(links[i])
			return _links
		else:
			return links
	
	def links_in_page_internal(self, link=None):
		try:
			if link is None:
				return self.links_in_page(count=1, filtred=True)[0]
			elif isinstance(link, str):
				links = self.links_in_page(count=None, filtred=True)
				links_filtred = list(filter(lambda x: str_filter_by_list(x, str(link)), links))
				if links_filtred:
					return links_filtred[0]
				else:
					return links[0]
			else:
				pass
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log('Exception', ex, level='warning')
			raise ex


class NavigatorMove(NavigatorHelper):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
	def scroll_by_offset(self, offset_x=None, offset_y=None, step_x=50, step_y=None):
		step_y = step_y if step_y else choice([100, 150, 200, 250, 300, 350, 400])
		if offset_x is None:
			_range = list(range(
				-self.Coordinator.left(),
				self.Coordinator.right(),
				step_x if step_x > 0 else 10
			))
			if _range:
				offset_x = choice(_range)
			else:
				offset_x = 0
		if offset_x != 0:
			offset_x = min(offset_x, self.Coordinator.right()) if offset_x > 0 else -min(abs(offset_x), self.Coordinator.left())
			for s in chunk_count_to_list(offset_x, step_x):
				self.Operator.scroll_page(s, 0)
				self.sleep_mouse_drag(0.3, 3)
		if step_y == 'rand':
			step_y = choice([
				randint(50, 150),
				randint(100, 200),
				randint(200, 400),
			])
			if random_triger_with_desp(0.3):
				step_y = -1 * step_y
		if offset_y is None:
			_range = list(range(
				-self.Coordinator.top(),
				self.Coordinator.bottom(),
				step_y if step_y > 0 else 10
			))
			if _range:
				offset_y = choice(_range)
			else:
				offset_y = 0
		if offset_y != 0:
			offset_y = min(offset_y, self.Coordinator.bottom()) if offset_y > 0 else -min(abs(offset_y), self.Coordinator.top())
			for s in chunk_count_to_list(offset_y, step_y):
				self.Operator.scroll_page(0, s)
				self.sleep_mouse_drag(0.3, 3)
	
	def scroll_to_coordinates(self, coordinates=None, size=None, dx=0, dy=0, _slp=(0.7, 2.5)):
		if size is None:
			size = {'x': 0, 'y': 0}
		try:
			if coordinates is None:
				coordinates = {
					'x': randint(0, self.Coordinator.body_width()),
					'y': randint(0, self.Coordinator.body_height())
				}
			
			# TODO refactoring
			left = max(0, coordinates['x'] - dx)
			right = min(self.Coordinator.body_width(), coordinates['x'] + size['x'] + dx)
			
			top = max(0, coordinates['y'] - dy)
			bottom = min(self.Coordinator.body_height(), coordinates['y'] + size['y'] + dy)
			
			offset_x = 0
			if left < self.Coordinator.left():
				offset_x = left - self.Coordinator.left()
			if right > self.Coordinator.rightline():
				offset_x = right - self.Coordinator.rightline()
			
			offset_y = 0
			if top < self.Coordinator.top():
				offset_y = top - self.Coordinator.top()
			if bottom > self.Coordinator.downline():
				offset_y = bottom - self.Coordinator.downline()
			
			self.scroll_by_offset(offset_x, offset_y)
			# TODO recursion
			
			try:
				slp(*_slp)
			except Exception as _ex:
				pass
			
			return None
		
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log('Exception', ex, level='warning')
			return None
	
	def scroll_to_top(self, percent=uniform(0.8, 1.0)):
		try:
			offset_y = int((0 - self.Coordinator.top() + 50) * percent)
			return self.scroll_by_offset(offset_y=offset_y)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			return None
	
	def scroll_to_down(self, percent=uniform(0.8, 1.0)):
		try:
			offset_y = int((self.Coordinator.bottom() - self.Coordinator.downline() - 50) * percent)
			return self.scroll_by_offset(offset_y=offset_y)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			return None
	
	def mouse_move_to_point(self, point):
		try:
			if self.Coordinator.coordinates_check_workplace(point) is False:
				self.scroll_to_coordinates(coordinates=point, dx=20, dy=50)
		except Exception as ex:
			log('Exception', ex, point, level='warning')
			raise ex
		curve = self.MouseCurve.track_from_2point(self.Operator.cursor(), point, self.Coordinator.current_workplace())
		self.Operator.mouse_move_by_track(curve)
	
	def mouse_move_to_element(self, elm):
		if not self.Coordinator.avalible_check_element(elm):
			log('Waring elm Over Left or Top', elm.location, level='warning')
			return None
		if self.Coordinator.workplace_check_element(elm) is False:
			self.scroll_to_coordinates(coordinates=elm.location, size=sizer(elm.size), dx=20, dy=50)
		curve = self.MouseCurve.track_from_2point(self.Operator.cursor(), elm.location, self.Coordinator.current_workplace())
		self.Operator.mouse_move_by_track(curve)
	
	def mouse_move_to_random(self, count=1, fullsize=False):
		for i in range(count):
			point = self.Coordinator.coordinates_get_random(fullsize=fullsize)
			# TODO Fullsize Fuck
			self.mouse_move_to_point(point)
	
	def move_to_element_around(
			self,
			elm,
			paddings=None,
			paddings_probability=0.4,
			percent=True,
			inside=False
	):
		if elm is None:
			raise Exception('element is None')
		
		if inside:
			paddings = [-50]
		else:
			if not paddings:
				paddings = [p for p in [600, 550, 450, 400, 300, 100, 50, 0] if random_triger_with_desp(paddings_probability)]
			paddings.append(-50)
		
		self.Operator.cursor_check_to_workplace()
		
		if self.Coordinator.workplace_check_element(elm) is False:
			log('elm not in workplace', elm)
			self.scroll_to_coordinates(coordinates=elm.location, size=sizer(elm.size), dx=20, dy=50)
		
		for padding in paddings:
			try:
				place = self.Coordinator.place_under_element(
					elm=elm,
					dx=padding,
					dy=padding,
					percent=percent
				)
				self.Operator.mouse_move_to_place(place)
			except Exception as ex:
				log('Exception mouse_move_to_place', ex, level='warning')
	
	def sleep_mouse_drag(self, a=0.3, b=30, delta=150):
		sleeps = random_chunk_distance(a, b)
		for _slp in sleeps:
			slp(_slp)
			if random_triger_with_desp(0.3):
				_place = self.Coordinator.place_under_coordinates(self.Operator.cursor(), dx=delta, dy=delta, percent=False)
				_point = self.Coordinator.get_coordinates_in_place(_place)
				self.mouse_move_to_point(_point)
		pass


class NavigatorClick(NavigatorMove):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
	def click_on_element(self, elm: WebElement, target_url=None):
		# TODO много раз кликает надо сделать отдельно клик по элементу и клик по урлу с проверкой табс
		click_methods = [
			('click_on_place_element', self.Operator.click_on_place_element),
			('click_on_element', self.Operator.click_on_element),
			('element_click_js', self.Elementor.element_click_js),
			('e.click()', lambda e: e.click())
		]
		result = False
		self.add_history('click')
		for (name, method) in click_methods:
			try:
				self.Operator.mouse_teleport_to_element(elm)
				elm_on_coordinates = self.Operator.element_on_cursor()
				
				self.Elementor.element_border_perple(elm_on_coordinates)
				# TODO сделать опцию => self.Elementor.element_display_block(elm_on_coordinates)
				self.Elementor.element_top(elm_on_coordinates)
				self.tabs_memory_url()
				self.tabs_memory_handles()
				log('try CLICK method', name)
				method(elm_on_coordinates)
				slp(2)
				if self.Elementor.element_has_focus(elm_on_coordinates):
					log('element_has_focus')
					# TODO не всегда срабатывает проверка и может несколько раз кликать одну ссылку
					self.Elementor.element_border_yellow(elm_on_coordinates)
					result = True
					break
				log('element_has_focus NOT')
				if target_url:
					if self.tab_check_target(target_url):
						log('tab_check_target YES', target_url)
						result = True
						break
					log('tab_check_target NOT')
				log('target_url', target_url)
				if self.tabs_compare_handles() or self.tabs_compare_url():
					log('tabs_compare_handles YES')
					result = True
					break
				log('tabs_compare_handles NOT')
				slp(2)
				self.Elementor.element_border_black(elm_on_coordinates)
			except (HTTPError, HTTPException) as ex:
				log('Exception HTTP', ex, level='warning')
				raise ex
			except (NoSuchElementException, StaleElementReferenceException) as _ex:
				log(f'Warning NoSuchElementException, StaleElementReferenceException', level='warning')
			except JavascriptException as ex:
				log(f'Warning JavascriptException, ex={ex}', level='warning')
			except Exception as ex:
				log('Exception', ex, level='warning')
				self.Elementor.press_esc()
		slp(2, 4)
		self.Operator.page_clear()
		return result
	
	def click_on_element_by_selector(self, selector, target_url=None):
		elm = self.get_element(selector)
		if not self.Operator.element_on_cursor_equal_selector(selector):
			self.Operator.mouse_teleport_to_element(elm)
		return self.click_on_element(elm, target_url=target_url)


class NavigatorActions(NavigatorClick):
	def __init__(self, driver: WebDriver, *args, **kwargs):
		super().__init__(driver, *args, **kwargs)
	
	def click_to_element(self, elm, target_url=None, paddings=None, percent=True):
		if not self.Coordinator.avalible_check_element(elm):
			log('Waring elm Over Left or Top', elm.location, level='warning')
			return None
		if elm is None:
			log('Waring elm is None', level='warning')
			return None
		if paddings is None:
			paddings = [150, 0]
		self.Operator.page_clear()
		if self.Elementor.element_has_focus(elm) and self.check_history():
			return True
		self.Elementor.element_border_blue(elm)
		
		self.move_to_element_around(elm, paddings=paddings, percent=percent)
		slp(1, 3)
		result = self.click_on_element(elm, target_url=target_url)
		slp(3, 7)
		self.Operator.page_clear()
		return result
	
	def send_tab(self, rand=False):
		if rand:
			if choice([True, False]):
				self.Elementor.element_press_tab()
				self.add_history('tab')
		else:
			self.Elementor.element_press_tab()
			self.add_history('tab')
	
	def click_to_element_force(self, elm, target_url, force=False):
		for i in range(3):
			log('click_to_element_force TRY', i)
			result = self.click_to_element(elm, target_url=target_url)
			slp(3)
			if self.tab_check_target(target_url) or result:
				return True
		if force:
			return self.site_check_in_tabs(target_url)
		return False
	
	def print_or_insert_to_element(self, elm, value, insert=False, clear=True, append=False):
		# TODO проверку в отдельную функцию isEmpty
		if not elm or not value:
			log(f'Exception not elm={elm} or not value={value}', level='warning')
			return None
		try:
			self.click_to_element(elm)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
		
		try:
			self.Elementor.printing(elm, value, insert=insert, clear=clear, append=append)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
		
		return value
	
	def print_or_insert_to_selector(
			self,
			selector=None,
			value='',
			enter_after=False,
			insert=False,
			clear=True,
			append=False,
			key_switch=False,
			to_eng=True,
			*args, **kwargs
	):
		if isinstance(value, (list, tuple)):
			value = choice(value)
		if key_switch:
			value_mutable = keyboard_change(value, to_eng=to_eng)
			value = choice([value, value_mutable])
		for i in range(10):
			elm = self.get_element(selector, *args, **kwargs)
			if elm is None:
				log('Exception elm is None', selector, level='warning')
				break
			self.print_or_insert_to_element(elm, value, insert=insert, clear=clear, append=append)
			if elm.get_attribute('value') == value:
				if enter_after:
					self.Elementor.element_press_enter(elm)
					slp(4, 7)
					self.Operator.page_clear()
				return value
		return value
	
	def insert_to_selector(self, selector=None, value='', enter_after=False, key_switch=False, to_eng=True):
		return self.print_or_insert_to_selector(
			selector=selector,
			value=value,
			enter_after=enter_after,
			insert=True,
			key_switch=key_switch,
			to_eng=to_eng
		)
	
	def print_to_selector(self, selector=None, value='', enter_after=False, key_switch=False, to_eng=True, *args, **kwargs):
		return self.print_or_insert_to_selector(
			selector=selector,
			value=value,
			enter_after=enter_after,
			key_switch=key_switch,
			to_eng=to_eng,
			*args, **kwargs
		)
	
	def print_or_insert(self, selector=None, value='', enter_after=False, key_switch=False, to_eng=True):
		return self.print_or_insert_to_selector(
			selector=selector,
			value=value,
			enter_after=enter_after,
			insert=choice([True, False]),
			key_switch=key_switch,
			to_eng=to_eng
		)
	
	def print_validate_to_selector(self, selector=None, selector_validate=None, value='', enter_after=False):
		elm = self.get_element(selector)
		if elm is None:
			log('Exception elm is None', selector, level='warning')
			return None
		result_value = ''
		value = str(value)
		if value:
			self.click_to_element(elm)
			try:
				for char in value:
					if self.get_element(selector_validate) or not result_value:
						self.Elementor.printing(elm, char, clear=False)
						result_value += char
					else:
						break
			except Exception as ex:
				log(f'Exception', ex, level='warning')
				pass
			if enter_after:
				self.Elementor.element_press_enter(elm)
				slp(4, 7)
				self.Operator.page_clear()
		return result_value
	
	def select_option_to_selector(self, selector_options=None, selector_select=None, except_option_index=None):
		if except_option_index is None:
			except_option_index = [-1]
		select = self.get_element(selector_select)
		options = self.get_elements(selector_options)
		if not options or options is None:
			log('Exception elm is None', selector_options, level='warning')
			return None
		for _index in except_option_index:
			options.pop(_index)
		try:
			option = choice(options)
			text = option.text
			selector = Select(select)
			selector.select_by_visible_text(text)
			return text
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
			return None
	
	def select_option_validate_to_selector(self, selector_options=None, selector_validate=None):
		error_validate = self.get_element(selector_validate)
		# TODO убрать в сценарии
		if error_validate is None:
			return True
		options = self.get_elements(selector_options)
		if not options:
			log('Exception elms is None', selector_options, level='warning')
			return None
		try:
			option = choice(options)
			text = option.text
			self.click_to_element(option)
			return text
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			return None
	
	def click_validate_fields(self, selector=None):
		while True:
			elms = self.get_elements(selector)
			if not elms:
				break
			for elm in elms:
				if elm:
					self.click_and_enter_element(elm)
			slp(2, 4)
		return True
	
	def click_to_selector(self, selector=None, *args, **kwargs):
		elm = self.get_element(selector, *args, **kwargs)
		if elm is None:
			log('Exception elm is None', selector, level='warning')
			return None
		handles = self.Driver.window_handles
		try:
			url = elm.get_attribute('href')
		except Exception as ex:
			log(f'Info', ex, level='info')
			url = None
		self.click_to_element(elm, url)
		new_handle = set(self.Driver.window_handles) - set(handles)
		if new_handle:
			self.Driver.switch_to.window(list(new_handle)[0])
		slp(2, 4)
		return self.current_url()
	
	def click_to_url(self, selector, url, link_blanc_off=True):
		result = False
		for i in range(3):
			elm = self.get_element(selector)
			if elm is None:
				log('Warning elm is None', selector, url, level='warning')
			else:
				if link_blanc_off:
					self.Elementor.link_blanc_off(elm)
				result = self.click_to_element(elm, target_url=url)
			if self.current_url_check(url) or result:
				return self.current_url()
			slp(2, 4)
		self.site_check(url)
		return self.current_url()
	
	def click_to_random_link(self, link=None):
		link = self.links_in_page_internal(link)
		self.click_to_element(link)
		pass
	
	def site_check_in_tabs(self, url):
		if self.tab_check_target(url):
			log(f'url {url} in tabs')
			self.tab_get_target(url)
			return True
		log(f'url {url} NOT in tabs')
		self.site_open(url)
		if self.tab_check_target(url):
			log(f'url {url} in tabs')
			self.tab_get_target(url)
			return True
		log(f'url {url} NOT in tabs')
		return False
	
	def click_and_enter_element(self, elm):
		self.click_to_element(elm)
		self.Elementor.element_press_enter(elm)
	
	def click_and_enter_selector(self, selector):
		self.click_and_enter_element(self.get_element(selector))


class NavigatorWorker(NavigatorActions):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
	def _read_page(self, offsets):
		_down_line = self.Coordinator.downline()
		for _offset in offsets:
			if not self.timer_get():
				break
			self.scroll_by_offset(offset_y=int(_offset))
			_slp = choice([
				(20, 40),
				(20, 50),
				(20, 70),
			])
			self.sleep_mouse_drag(*_slp, delta=42)
			if random_triger_with_desp(0.3):
				self.mouse_move_to_random(fullsize=False)
			if self.Coordinator.downline() == _down_line:
				log('Exception scroll not work', level='warning')
				break
	
	def site_read_page(self, target_url=None):
		log('SITE_READ_PAGE')
		slp(2, 4)
		self.Operator.page_clear()
		url = self.current_url()
		if clean_url(url) == get_domain_from_url(target_url):
			self.click_to_random_link()
		_bottom = self.Coordinator.bottom() - 50
		scroll_chunks_down = random_chunk_distance(_bottom * uniform(0.55, 0.8), _bottom * uniform(0.81, 0.93))
		self._read_page(scroll_chunks_down)
		
		_top = self.Coordinator.top() - 50
		scroll_chunks_up = -1 * (random_chunk_distance(_top * uniform(0.55, 0.8), _top * uniform(0.81, 0.93)))
		self._read_page(scroll_chunks_up)
		slp(2, 4)
		self.Operator.page_clear()
		if url != self.current_url():
			self.Operator.cursor_rnd()
		return True
	
	def site_read_time(self, target_url=None, time_on_site=240):
		self.timer_set(time_on_site)
		while self.timer_get():
			self.Operator.page_clear()
			self.site_read_page(target_url)
		return True
	
	def search_key(self, key, selector_input, selector_button=None, append=False):
		log('search_key', key)
		url = str(self.current_url())
		search_input = self.Selector.select_one(selector=selector_input)
		if search_input is not None:
			self.screenshot_save()
			self.click_to_element(search_input)
		
		search_input = self.Selector.select_one(selector=selector_input)
		if search_input is not None:
			self.screenshot_save()
			self.Elementor.printing(search_input, key, append=append)
			self.screenshot_save()
			search_button = self.Selector.select_one(selector=selector_button)
			if search_button is None or choice([True, False]):
				self.Elementor.element_press_enter(search_input)
				slp(2, 4)
				self.Operator.page_clear()
			else:
				self.click_to_element(search_button)
			if self.current_url() == url:
				self.Elementor.element_press_enter(search_input)
				slp(2, 4)
				self.Operator.page_clear()
			slp(1)
		return True
	
	def region_set(self, selector, region=None):
		log('region_set', region)
		if region is None or int(region) == -2:
			return True
		else:
			region = int(region)
		region_input = self.Selector.select_one(selector=selector)
		if region_input is not None:
			return self.Injector.cmd_inject('element_set_value', execute_args=region_input, script_args=region)
		return False
	
	def search_get_results(self, selector_search_result_list, selector_search_result_link, selector_static, target_url, count_others=0):
		self.Elementor.elements_set_position_static(selector_static)
		if target_url is None:
			log('Warning target_url is None', level='warning')
		result_list = self.Selector.select(selector=selector_search_result_list)
		links = []
		for result_item in result_list:
			link = self.Selector.select_one(selector=selector_search_result_link, obj=result_item)
			links.append(link)
		
		if target_url:
			target_link = self.Selector.select_one(selector=f'a[href*={get_domain_from_url(target_url)}]')
			if target_link:
				links.append(target_link)
		
		if not links:
			log('Warning нет сайтов в выдаче')
			self.page_save_html()
			slp(1)
			return None, []
		
		_sites = []
		for link in links:
			url = link.get_attribute('href')
			if url:
				_domain = get_domain_from_url(url)
				if str_filter_by_list(_domain, STOP_HREF) is False:
					_sites.append(
						[
							link,
							url,
							False
						]
					)
		
		_target = None
		_results = []
		log('_sites', _sites)
		if _sites:
			shuffle(_sites)
			try:
				_target_urls = list(filter(lambda x: x[1].find(target_url) > -1, _sites))
			except Exception as ex:
				log(f'Exception', ex, level='warning')
				_target_urls = None
			
			if _target_urls:
				_target_urls.sort(key=lambda x: len(x[1]), reverse=True)
				try:
					_target = _sites.pop(_sites.index(_target_urls[0]))
					log('_target', _target)
				except Exception as ex:
					log(f'Exception', ex, level='warning')
					_target = None
				for _target_url in _target_urls:
					try:
						_sites.pop(_sites.index(_target_url))
					except Exception as _ex:
						# TODO check fail is not in list
						pass
			
			try:
				# выбираем конкурентов максимум из доступных если count_others больше чем есть вариантов
				_count = randint(1, min(max(len(_sites), 1), count_others))
				_results = _sites[:_count]
			except Exception as _ex:
				pass
			
			if _target is None:
				log('Warning нет целевого')
				try:
					log(list(map(lambda x: x[1], _sites)))
				except Exception as ex:
					log(f'Exception', ex, _sites, level='warning')
					pass
				self.page_save_html()
				slp(1)
			else:
				_target[2] = True
		shuffle(_results)
		return _target, _results
	
	def search_open_results(self, target=None, others_site=None):
		if others_site is None:
			others_site = []
		target_url = None
		if target is not None:
			others_site.append(target)
			target_url = target[1]
			log('target_url', target_url)
		handle_search = self.Driver.current_window_handle
		for site in others_site:
			# TODO: убрать передачу элементов, передвать селекторы
			self.click_to_element_force(*site)
			try:
				self.Driver.switch_to.window(handle_search)
			except Exception as _ex:
				log("Exception don't can switch to search", level='warning')
		log('target_url', target_url)
		# self.tabs_close_except(target_site, False)
		self.tabs_close_except(target_url)
		self.tab_get_target(target_url)
	
	def search_open_results_and_read(self, sites=None, time_on_site=60):
		if sites is None:
			sites = []
		handle_search = self.Driver.current_window_handle
		for site in sites:
			self.click_to_element_force(*site)
			slp(4, 8)
			try:
				self.tab_get_target(site[1])
				if not self.get_element('body'):
					log('Exception not Body', level='warning')
					return False
				self.site_read_time(site[1], time_on_site=time_on_site)
				self.tab_close()
			except Exception as _ex:
				log("Exception don't can read site", site, level='warning')
			try:
				self.Driver.switch_to.window(handle_search)
			except Exception as _ex:
				log("Exception don't can switch to search", level='warning')
			pass
	
	def click_and_read(self, selector, time_on_site=60):
		current_url = self.click_to_selector(selector)
		self.site_read_time(current_url, time_on_site=time_on_site)
		return True


class Navigator(NavigatorWorker):
	def __init__(self, driver: WebDriver, *args, **kwargs):
		super().__init__(driver, *args, **kwargs)
		self.init()

