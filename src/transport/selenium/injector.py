import os
from http.client import HTTPException

from css_html_js_minify import js_minify
from itools.rewr.tools import file_to_text
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, JavascriptException
from urllib3.exceptions import HTTPError

from .config import log, CONF
from .constants.injector import JS_CMD
from .selector import Selector

__all__ = ('Injector',)

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
JS_HELPER = file_to_text(CURRENT_DIR + '/static/jss/helper.js')
TRAIL = js_minify(file_to_text(CURRENT_DIR + '/static/jss/trail.js'))
XPATH = js_minify(file_to_text(CURRENT_DIR + '/static/jss/xpath.js'))
JQUERY = file_to_text(CURRENT_DIR + '/static/jss/jquery-3.1.1.min.js')
HEATMAP_SCRIPT = file_to_text(CURRENT_DIR + '/static/jss/heatmap.min.js')
HEATMAP_DRAW = js_minify(file_to_text(CURRENT_DIR + '/static/jss/heatmap-draw.js'))


class InjectorBase:
	def __init__(self, driver: WebDriver):
		self.Driver = driver
		pass
	
	@staticmethod
	def js_execute(executor, script, args=None):
		try:
			if args:
				return executor(script, *args)
			else:
				return executor(script)
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			# raise ex
			return None
		except (NoSuchElementException, StaleElementReferenceException) as _ex:
			log(f'Exception NoSuchElementException, StaleElementReferenceException  script={script}, args={args}', level='warning')
			return None
		except JavascriptException as ex:
			log(f'Exception JavascriptException script={script[:50]}, ex={ex}', level='warning')
			return None
		except Exception as ex:
			log('Exception', script, args, ex, level='warning')
			return None
	
	def js_inject(self, script, args=None, execute_async=False):
		if execute_async:
			_executor = self.Driver.execute_async_script
		else:
			_executor = self.Driver.execute_script
		if args is not None and not isinstance(args, (tuple, list)):
			args = (args,)
		if isinstance(script, list):
			result = []
			for _script in script:
				_result = self.js_execute(_executor, _script, args)
				result.append(_result)
			return result
		return self.js_execute(_executor, script, args)
	
	def cmd_inject(self, cmd, execute_args=None, script_args=None, script_kwargs=None, execute_async=False):
		if script_args is not None and not isinstance(script_args, (tuple, list)):
			script_args = (script_args,)
		cmd_tpl = JS_CMD.get(cmd)
		if cmd_tpl is None:
			return None
		try:
			if script_args and script_kwargs:
				script = cmd_tpl.format(*script_args, **script_kwargs)
			elif script_args:
				script = cmd_tpl.format(*script_args)
			else:
				script = cmd_tpl
			return self.js_inject(script, args=execute_args, execute_async=execute_async)
		except (HTTPError, HTTPException) as ex:
			log('Exception HTTP', ex, level='warning')
			return None
		except Exception as ex:
			log(
				f'Exception cmd ={cmd} cmd_tpl={cmd_tpl} execute_args={execute_args} script_args={script_args}, script_kwargs={script_kwargs}',
				ex,
				level='warning'
			)
			return None
	
	def cmd_inject_arg(self, cmd, execute_args=None, script_args=None, script_kwargs=None, execute_async=False):
		return self.cmd_inject(cmd, execute_args, script_args, script_kwargs, execute_async=execute_async)
	
	def cmd_inject_arg_list(self, cmd, execute_args=None, script_args=None, script_kwargs=None, execute_async=False):
		if script_args is None:
			script_args = []
		if isinstance(script_args, str):
			script_args = [script_args]
		result = []
		for _script_args in script_args:
			_result = self.cmd_inject(cmd, execute_args, _script_args, script_kwargs, execute_async=execute_async)
			result.append(_result)
		return result
	
	def cmd_inject_nolog(self, cmd, script_args=None, script_kwargs=None, execute_async=False):
		return self.cmd_inject(cmd, script_args, script_kwargs, execute_async=execute_async)


class InjectorScript(InjectorBase):
	def __init__(self, driver: WebDriver):
		super().__init__(driver)
		self.Selector = Selector(self.Driver)
	
	def jquery_set(self):
		return self.js_inject(JQUERY)
	
	def jqury(self):
		if 'jquery' not in self.Driver.page_source:
			self.jquery_set()
	
	def helper_set(self):
		return self.cmd_inject('js_helper_set', script_args=(JS_HELPER,))
	
	def helper(self):
		if self.Selector.select_one(selector='#js_helper_coordinator', wait=1) is None:
			self.helper_set()
	
	def heatmap_set(self, body_height):
		return self.cmd_inject('heatmap_set', script_args=(body_height, HEATMAP_SCRIPT, HEATMAP_DRAW))
	
	def heatmap(self, body_height):
		# TODO Selector
		if self.Selector.select_one(selector='#heatmapContainerWrapper', wait=1) is None:
			self.heatmap_set(body_height)
	
	def mouse_trail(self):
		if CONF.MOUSE_TRAIL:
			if self.Selector.select_one(selector='div.cursor_trail_points', wait=1) is None:
				return self.js_inject(TRAIL)
	
	def mouse_trail_off(self):
		return self.cmd_inject('mouse_trail_off')
	
	def xpather(self):
		# todo собрать все инжекты в один метод
		if self.Selector.select_one(selector='#selectorxpathcss', wait=1) is None:
			return self.cmd_inject('xpather_set', script_args=(XPATH,))


class Injector(InjectorScript):
	def __init__(self, driver: WebDriver):
		super().__init__(driver)
	
	def selector_on_point(self, point):
		if CONF.SELECTOR.lower() == 'xpath':
			selector = self.cmd_inject('xpath_on_coordinates', script_args=(point['x'], point['y']))
		elif CONF.SELECTOR.lower() == 'css':
			selector = self.cmd_inject('css_on_coordinates', script_args=(point['x'], point['y']))
		else:
			log('Exception selector type==', CONF.SELECTOR, level='warning')
			selector = None
		return selector
