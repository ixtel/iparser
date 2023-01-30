from itools.configure_init import init_config_app

from ... import config as config_main

__all__ = ('ConfigBase', 'CONF', 'log', 'iloger')


class ConfigApp:
	DEBUG = False
	APP_NAME = 'iParser.Selenium'


class ConfigMain:
	SELECTOR = 'CSS'
	
	SCREENSHOT = False
	
	ERROR_PAGE_SAVE = False
	
	# TODO SEARCH в админку
	SEARCH = {
		'yandex': 'https://ya.ru',
		'google': 'https://google.ru',
	}


class ConfigLoger:
	LOGER_SAVE = False
	LOGER_STACK = False
	LOGER_STACK_FULL = False
	LOGER_DISABLE = False
	LOGER_PATH = 'c:/dev_log'
	LOGER_LEVEL = 'info'


class ConfigDriver:
	MARIONETTE = False
	BROWSER = 'firefox'
	HEADLESS = True
	
	PROCESS_PATH = 'seledroid'
	
	FIREFOX_DRIVER = 'c:/SeleDroid/geckodriver.exe'
	FIREFOX_PROFILE = 'r:/SeleDroid/firefox/profile/default'
	FIREFOX_BINARY = 'r:/SeleDroid/firefox/browser/firefox.exe'


class ConfigNavigator:
	MOUSE_TRAIL = True
	ELEMENT_STYLER = False
	SELECTOR = 'CSS'
	
	ERROR_PAGE_SAVE = False
	LOG_JS_INJECT = False
	
	SCREENSHOT = False
	ANGREE = False


class ConfigTimeout:
	TIMEOUT_PAGE_LOAD = 45
	TIMEOUT_SET_SCRIPT = 45
	TIMEOUT_WAIT_ELM = 15


class ConfigBase(ConfigApp, ConfigMain, ConfigLoger, ConfigDriver, ConfigTimeout):
	pass


CONF, iloger = init_config_app(
	None,
	(config_main.CONF, ConfigBase)
)

log = iloger.log
