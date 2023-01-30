from itools.configure_init import init_config_app

__all__ = ('ConfigBase', 'CONF', 'log', 'iloger')


class ConfigApp:
	DEBUG = False
	APP_NAME = 'iParser'
	
	LOGER_SAVE = False
	LOGER_STACK = False
	LOGER_STACK_FULL = False
	LOGER_DISABLE = False
	LOGER_PATH = 'c:/dev_log'
	LOGER_LEVEL = 'info'


class ConfigBase(ConfigApp):
	pass


CONF, iloger = init_config_app(
	None,
	ConfigBase,
	get_loger=True
)

log = iloger.log
