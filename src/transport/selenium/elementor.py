from http.client import HTTPException
from random import choice

from itools.dataminer.imath import random_triger_with_desp
from itools.timer.tools import slp
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, JavascriptException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from urllib3.exceptions import HTTPError

from .config import log, CONF
from .constants.selector import BLOCKS_REMOVE, BLOCKS_CLOSE, SEARCH
from .injector import Injector

__all__ = ('Elementor',)


class Elementor:
	def __init__(self, driver: WebDriver):
		self.Driver = driver
		self.Injector = Injector(self.Driver)
		pass
	
	def element_has_focus(self, elm):
		active_element = self.Driver.switch_to.active_element
		return elm == active_element
	
	def elements_remove(self, selectors=BLOCKS_REMOVE):
		self.Injector.cmd_inject_arg_list('element_clean', selectors)
	
	def element_click_js(self, elm):
		self.Injector.cmd_inject_arg('element_click_js', elm)
	
	def elements_click_jscss(self, selectors=BLOCKS_CLOSE):
		self.Injector.xpather()
		self.Injector.cmd_inject_arg_list('element_click_jscss', script_args=selectors)
	
	def elements_set_position_static(self, selectors=SEARCH['yandex'].get('block_flow')):
		self.Injector.helper()
		self.Injector.cmd_inject_arg_list('element_position_static', script_args=selectors)
	
	def link_blanc_off(self, elm):
		return self.Injector.cmd_inject_arg('link_blanc_off', elm)
	
	def element_display_block(self, elm):
		return self.Injector.cmd_inject('element_style', execute_args=elm, script_args=('display', 'block'))
	
	def element_top(self, elm):
		if CONF.ELEMENT_STYLER:
			return self.Injector.cmd_inject('element_top', execute_args=elm)
		else:
			return None
	
	def element_border(self, elm, color):
		if CONF.ELEMENT_STYLER:
			try:
				return self.Injector.cmd_inject('element_border', execute_args=elm, script_args=color)
			except (HTTPError, HTTPException) as ex:
				log('Exception HTTP', ex, level='warning')
				raise ex
			except (NoSuchElementException, StaleElementReferenceException) as _ex:
				log(f'Warning NoSuchElementException, StaleElementReferenceException', level='warning')
				return None
			except JavascriptException as ex:
				log(f'Warning JavascriptException, ex={ex}', level='warning')
				return None
			except Exception as ex:
				log('Exception', ex, level='warning')
				return None
		else:
			return None
	
	def element_border_red(self, elm):
		self.element_border(elm, 'F00')
	
	def element_border_blue(self, elm):
		self.element_border(elm, '07bed8')
	
	def element_border_green(self, elm):
		self.element_border(elm, '0F0')
	
	def element_border_yellow(self, elm):
		self.element_border(elm, 'd1bb1f')
	
	def element_border_black(self, elm):
		self.element_border(elm, '000')
	
	def element_border_perple(self, elm):
		self.element_border(elm, 'd900ea')
	
	@staticmethod
	def element_info(elm, head=False):
		if head:
			log('elm - %s', head)
		log('elm - text %s', elm.text)
		log('elm - location %s', elm.location)
		log('elm - size %s', elm.size)
	
	
	@staticmethod
	def send_keys_element(elm, key):
		try:
			elm.send_keys(key)
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except (NoSuchElementException, StaleElementReferenceException, JavascriptException) as _ex:
			log(f'Exception NoSuchElementException, StaleElementReferenceException, JavascriptException', level='warning')
			return None
		except Exception as ex:
			log('Exception', ex, level='warning')
			return None
	
	
	def clear_input(self, elm):
		if random_triger_with_desp(0.3):
			self.send_keys_element(elm, Keys.CONTROL + "a")
			slp(0.5, 1.2)
			self.send_keys_element(elm, Keys.DELETE)
			slp(0.5, 1.2)
		else:
			self.send_keys_element(elm, Keys.END)
			slp(0.4, 0.8)
			while len(elm.get_attribute('value')) > 0:
				self.send_keys_element(elm, Keys.BACK_SPACE)
				slp(0.4, 0.8)
	
	def selector_on_element(self, elm):
		try:
			if CONF.SELECTOR.lower() == 'xpath':
				selector = self.Injector.cmd_inject('xpath_on_element', elm)
			elif CONF.SELECTOR.lower() == 'css':
				selector = self.Injector.cmd_inject('css_on_element', elm)
			else:
				log('Exception selector type==', CONF.SELECTOR, level='warning')
				selector = None
			return selector
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except Exception as ex:
			log('Exception', ex, elm, level='warning')
			return None
	
	def printing(self, elm, text='', insert=False, clear=True, append=False):
		text = str(text)
		if not text:
			log(f'Warning text is Empty', level='warning')
			return elm
		try:
			val = elm.get_attribute('value')
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			val = None
			pass
		# TODO добавить харакетры. быстрей печатает, чаще мышкой делает промежуточных движений, пользуется в основном клавиатурой.
		try:
			if append:
				# если дописываем в уже заполненное поле, переводим каретку в конец
				self.send_keys_element(elm, Keys.END)
				if val:
					try:
						# убираем из добавочного запроса слова которые уже естьв поле ввода
						text_set = set(text.split(' '))
						text_set_diff = list(text_set - set(val.split(' ')))
						if len(text_set_diff) != len(text_set):
							text = ' '.join(text_set_diff)
					except Exception as ex:
						log(f'Exception', ex, level='warning')
						pass
			elif val and clear:
				# если в инпуте есть значение и печатание по символоно отключено и добавка к текущему отключено
				# очистим поле
				self.clear_input(elm)
			else:
				pass
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
		try:
			slp(0.5, 1.2)
			if insert:
				self.send_keys_element(elm, text)
			else:
				try:
					for k in text:
						self.send_keys_element(elm, k)
						slp(*choice([
							(0.05, 0.5),
							(0.06, 1),
							(0.07, 1.2),
							(0.08, 1.5),
							(0.09, 0.8),
							(0.1, 2),
						]))
				except Exception as ex:
					log(f'Exception', ex, level='warning')
					pass
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
		return elm
	
	def send_keys(self, key):
		try:
			ActionChains(self.Driver).send_keys(key).perform()
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			raise ex
		except (NoSuchElementException, StaleElementReferenceException) as _ex:
			log(f'Exception NoSuchElementException, StaleElementReferenceException', level='warning')
			return None
		except JavascriptException as ex:
			log(f'Exception JavascriptException, ex={ex}', level='warning')
			return None
		except Exception as ex:
			log('Exception', ex, level='warning')
			return None
	
	def element_press_enter(self, elm):
		self.send_keys_element(elm, Keys.ENTER)
		slp(0.1, 0.7)
	
	def element_press_tab(self, elm=None):
		if elm is None:
			elm = self.Driver.switch_to.active_element
		self.send_keys_element(elm, Keys.TAB)
		slp(0.1, 0.7)
	
	def press_esc(self):
		self.send_keys(Keys.ESCAPE)
		slp(0.1, 0.7)
