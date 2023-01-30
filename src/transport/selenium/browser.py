import os
import signal
import time
from http.client import HTTPException
from typing import Union

from itools.timer.tools import slp
from itools.rewr.tools import text_to_file
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from urllib3.exceptions import HTTPError

from .config import log, CONF

__all__ = ('Browser',)


class Browser:
	def __init__(self, driver: Union[WebDriver, webdriver.Firefox, webdriver.Chrome], unit_id=None, *args, **kwargs):
		self.Driver = driver
		if unit_id is None:
			unit_id = int(time.time())
		self.item_dir = f'{CONF.DATA_DIR}/data/queue/{unit_id}'
		
		self._pid = int(time.time())
		
		self._dir_save_html = f'{self.item_dir}/pages'
		os.makedirs(os.path.dirname(self._dir_save_html), exist_ok=True)
		
		self._dir_save_screens = f'{self.item_dir}/screens'
		os.makedirs(os.path.dirname(self._dir_save_screens), exist_ok=True)
	
	@property
	def status(self):
		try:
			self.Driver.execute(Command.STATUS)
			return True
		except Exception as ex:
			log(ex)
			return False
	
	def wait_action(self):
		while True:
			if not self.status:
				break
			slp(10)
	
	def screenshot_save(self, name=None):
		if CONF.SCREENSHOT:
			try:
				name = str(name) if name else f'{self._pid}_{int(time.time())}'
				try:
					self.Driver.save_screenshot(f'{self._dir_save_screens}/{name}.png')
					return name
				except (HTTPError, HTTPException) as ex:
					log('Exception HTTP', ex, level='warning')
					raise ex
				except Exception as ex:
					log('Exception', ex, level='warning')
					return str(ex)
			except Exception as ex:
				log(f'Exception', ex, level='warning')
				raise ex
	
	def page_save_html(self):
		if CONF.ERROR_PAGE_SAVE:
			text_to_file(self.Driver.page_source, self._dir_save_html + f'/{self._pid}_{int(time.time())}.html')
	
	def close(self):
		try:
			self.Driver.service.process.send_signal(signal.SIGTERM)
			self.Driver.quit()
		except Exception as _ex:
			try:
				self.Driver.quit()
			except Exception as ex:
				log('Exception', ex, level='warning')
		return None
	
	def __del__(self):
		self.close()
