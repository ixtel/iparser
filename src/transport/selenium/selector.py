from typing import Union
from http.client import HTTPException
from urllib3.exceptions import HTTPError
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Remote as WebDriver
from cssselect import GenericTranslator

from .config import log, CONF

__all__ = ('Selector',)


class Selector:
	def __init__(self, driver: WebDriver = None, selector_type=None, wait_elm_timeout=CONF.TIMEOUT_WAIT_ELM):
		self.Driver = driver
		if selector_type is None:
			selector_type = CONF.SELECTOR
		self.selector_type = selector_type.lower()
		self.wait_elm_timeout = wait_elm_timeout
		self.GenericTranslator = GenericTranslator()
	
	def css_to_xpath(self, css, prefix='descendant-or-self::'):
		try:
			return self.GenericTranslator.css_to_xpath(css=css, prefix=prefix)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			raise ex
	
	def _select(self, obj: WebDriver, selector: Union[str, list], exp_condition=expected_conditions.presence_of_all_elements_located, wait=None):
		if obj is None:
			return None
		if wait is None:
			wait = self.wait_elm_timeout
		try:
			if self.selector_type == 'xpath':
				_locator = (
					By.XPATH,
					self.css_to_xpath(selector)
				)
			elif self.selector_type == 'css':
				_locator = (
					By.CSS_SELECTOR,
					selector
				)
			else:
				log('Exception selector type==', self.selector_type, level='warning')
				return None
			try:
				elm = WebDriverWait(obj, int(wait)).until(
					exp_condition(_locator)
				)
			except (HTTPError, HTTPException) as ex:
				log('Exception HTTP', ex, level='warning')
				raise ex
			except Exception as ex:
				log(f'Exception _locator={_locator}', ex, level='debug')
				elm = None
			return elm
		except Exception as _ex:
			log(f'Exception, {_ex}', level='critical')
			return None
	
	@staticmethod
	def _select_prepare_result(elm, attr, attr_name):
		try:
			if elm is None:
				return None
			if attr is not None:
				try:
					_r = getattr(elm, attr)
				except Exception as ex:
					log(f'Exception', ex, level='warning')
					_r = None
			elif attr_name is not None:
				if attr_name.startswith('@'):
					try:
						_r = elm.get_property(attr_name[1:])
					except Exception as ex:
						log(f'Exception', ex, level='warning')
						_r = None
				else:
					try:
						_r = elm.get_attribute(attr_name)
					except Exception as ex:
						log(f'Exception', ex, level='warning')
						_r = None
			else:
				_r = elm
			return _r
		except Exception as ex:
			log(f'Exception', ex, level='critical')
			return None
	
	def select(
			self,
			obj: WebDriver = None,
			selector: Union[str, list] = None,
			attr: str = None,
			attr_name: str = None,
			exp_condition=expected_conditions.presence_of_all_elements_located,
			wait=None
	):
		if obj is None:
			obj = self.Driver
		if selector is None:
			selector = []
		
		if not isinstance(selector, list):
			selector = [selector]
		for p in selector:
			result = self._select(obj, p, exp_condition, wait=wait)
			if isinstance(result, list):
				_result = []
				for elm in result:
					_elm = self._select_prepare_result(elm, attr, attr_name)
					_result.append(_elm)
				if _result:
					return _result
			if result:
				return self._select_prepare_result(result, attr, attr_name)
		return None
	
	def select_one(self, obj: WebDriver = None, selector: Union[str, list] = None, attr: str = None, attr_name: str = None, wait=None):
		if obj is None:
			obj = self.Driver
		if selector is None:
			selector = []
		return self.select(
			obj=obj, selector=selector, attr=attr, attr_name=attr_name, exp_condition=expected_conditions.presence_of_element_located, wait=wait
		)
	
	def select_to_be_click(self, obj: WebDriver = None, selector: Union[str, list] = None, attr: str = None, attr_name: str = None, wait=None):
		if obj is None:
			obj = self.Driver
		if selector is None:
			selector = []
		return self.select(
			obj=obj, selector=selector, attr=attr, attr_name=attr_name, exp_condition=expected_conditions.element_to_be_clickable, wait=wait
		)
