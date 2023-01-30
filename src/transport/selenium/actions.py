from random import uniform, choice

from itools.network.tools import get_domain_from_url
from itexter.tools import transliterate
from itools.timer.tools import slp

from .config import log
from .constants.selector import SEARCH
from .navigator import Navigator

__all__ = ('Actions',)


class ActionsCustom:
	def __init__(
			self,
			navigator: Navigator,
			captcha_decode,
			search='yandex'
	):
		self.Navigator = navigator
		self.CaptchaDecode = captcha_decode
		self.SEARCH_SELECTOR = SEARCH.get(search, SEARCH.get('yandex', {}))
	
	def region_set(self, region):
		try:
			return self.Navigator.region_set(
				selector=self.SEARCH_SELECTOR.get('region_input'),
				region=region,
			)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
	
	def site_read(self, target_url=None, time_on_site=240):
		try:
			return self.Navigator.site_read_time(
				target_url=target_url,
				time_on_site=time_on_site
			)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
	
	def search_key(self, key, append=False):
		try:
			return self.Navigator.search_key(
				key=key,
				selector_input=self.SEARCH_SELECTOR.get('search_input', 'input'),
				selector_button=self.SEARCH_SELECTOR.get('search_button'),
				append=append
			)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
	
	def search_get_results(self, target_url, count_others=0):
		try:
			return self.Navigator.search_get_results(
				# selector_search_result=self.SEARCH_SELECTOR.get('search_result'),
				selector_search_result_list=self.SEARCH_SELECTOR.get('search_result_list'),
				selector_search_result_link=self.SEARCH_SELECTOR.get('search_result_link'),
				selector_static=self.SEARCH_SELECTOR.get('block_flow'),
				target_url=target_url,
				count_others=count_others
			)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
	
	def _search_site_nextpage(self):
		# todo url проверки не проходит потому что редиректит даже если открывается правильно
		try:
			nextpage_url = self.Navigator.Selector.select_one(selector=self.SEARCH_SELECTOR.get('search_next'), attr_name='href', wait=2)
			if not nextpage_url:
				log('Exception nextpage_url', level='warning')
				return None
			self.Navigator.click_to_url(selector=self.SEARCH_SELECTOR.get('search_next'), url=nextpage_url)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
	
	def search_key_deep(self, key, target_url, searchdeep, cookies_save_callback, count_others=0, append=False):
		_target = None
		_results = []
		try:
			self.CaptchaDecode.captcha_check()
			
			self.search_key(key, append=append)
			
			cookies_save_callback(self.Navigator.get_cookies())
			
			for i in range(int(searchdeep) + 1):
				slp(3, 7)
				self.CaptchaDecode.captcha_check()
				log('pagenum', i)
				
				self.Navigator.screenshot_save()
				_target, _results = self.search_get_results(target_url, count_others)
				log('_target', _target)
				log('_results', _results)
				
				cookies_save_callback(self.Navigator.get_cookies())
				
				if append is False or _target is None:
					self.Navigator.scroll_to_down(uniform(0.6, 0.8))
				if _target:
					log('Have target')
					break
				self.Navigator.screenshot_save()
				self._search_site_nextpage()
				slp(3, 5)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
		
		return _target, _results
	
	def search_site(
			self,
			search_url,
			key,
			target_url,
			searchdeep,
			cookies_save_callback,
			status_save_callback,
			region=None,
			count_others=0,
			recurse=False
	):
		_target = None
		_results = []
		try:
			if isinstance(search_url, str):
				# если уже открыт поисковик передается None
				self.Navigator.site_open(search_url)
			
			self.Navigator.screenshot_save()
			cookies_save_callback(self.Navigator.get_cookies())
			
			self.CaptchaDecode.captcha_check()
			
			self.region_set(region)
			
			_target, _results = self.search_key_deep(
				key=key,
				target_url=target_url,
				searchdeep=searchdeep,
				cookies_save_callback=cookies_save_callback,
				count_others=count_others
			)
			
			if _target or _results:
				cookies_save_callback(self.Navigator.get_cookies())
				if _target is None:
					# Если нет целевого сайта всеравно открываем другие если есть но оставляем поиск открытым
					self.Navigator.search_open_results([None, self.Navigator.current_url(), False], _results)
				else:
					status_save_callback('success')
					self.Navigator.search_open_results(_target, _results)
			if _target is None:
				status_save_callback('fail')
				# если нет целевого и других сайтов
				self.Navigator.screenshot_save()
				try:
					# пробуем добавить адрес сайта к запросу
					_target_url = choice([
						transliterate(target_url, lang='en_ru'),
						target_url,
						' '.join(target_url.split('.')),
					])
					
					_target, _results = self.search_key_deep(
						key=f' {_target_url}',
						target_url=target_url,
						searchdeep=searchdeep,
						cookies_save_callback=cookies_save_callback,
						count_others=0,
						append=True)
					
					if _target or _results:
						cookies_save_callback(self.Navigator.get_cookies())
						if _target:
							status_save_callback('success')
						else:
							status_save_callback('fail')
						self.Navigator.search_open_results(_target, _results)
					
					if _target is None and recurse is False:
						# если все же нет целевого и этот блок еще не вызывался(recursive)
						# открываем другой поисковик(работает только в яндексе, переход на гугл)
						try:
							searchengines_list = self.Navigator.Selector.select(selector=self.SEARCH_SELECTOR.get('searchengines_list'), wait=1)
							other_search = searchengines_list[1]
						except Exception as ex:
							log(f'Exception', ex, level='warning')
							other_search = None
						if other_search is not None:
							self.SEARCH_SELECTOR = SEARCH['google']
							self.Navigator.click_to_element_force(other_search, 'google.com', True)
							
							return self.search_site(
								search_url=None,
								key=key,
								target_url=target_url,
								searchdeep=searchdeep,
								cookies_save_callback=cookies_save_callback,
								status_save_callback=status_save_callback,
								region=region,
								count_others=count_others,
								recurse=True
							)
					else:
						status_save_callback('success')
				except Exception as ex:
					log(f'Exception', ex, level='warning')
					status_save_callback('fail')
					raise ex
		except Exception as ex:
			status_save_callback('fail')
			log('Exception search_site', ex, level='warning')
		return _target, _results
	
	def search_direct(self, search_url, target_url, cookies_save_callback, status_save_callback):
		# накрутка прямых переходов с внешних сайтов
		_target = None
		try:
			self.Navigator.site_open(search_url)
			self.Navigator.screenshot_save()
			cookies_save_callback(self.Navigator.get_cookies())
			
			links = self.Navigator.Selector.select(selector='a', wait=1)
			if links is not None:
				for link_elm in links:
					if link_elm is not None:
						url = link_elm.get_attribute('href')
						if url:
							if get_domain_from_url(url) == get_domain_from_url(target_url):
								_target = [link_elm, target_url, True]
			
			if _target is not None:
				self.Navigator.screenshot_save()
				status_save_callback('run')
				try:
					cookies_save_callback(self.Navigator.get_cookies())
					self.Navigator.search_open_results(_target, [])
					status_save_callback('success')
				except Exception as ex:
					log(f'Exception', ex, level='warning')
					status_save_callback('fail')
					raise ex
			else:
				status_save_callback('fail')
		except Exception as ex:
			log('Exception search_site', ex, level='warning')
		return _target, []


class Actions(ActionsCustom):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._actions_methods = dict(
			assert_exist=self.Navigator.get_element,
			assert_not_exist=self.Navigator.get_element,
			captcha_check=self.CaptchaDecode.captcha_check,
			click=self.Navigator.click_to_selector,
			click_to_url=self.Navigator.click_to_url,
			click_and_read=self.Navigator.click_and_read,
			insert=self.Navigator.insert_to_selector,
			mouse_move_to_random=self.Navigator.mouse_move_to_random,
			open_page=self.Navigator.site_open,
			print=self.Navigator.print_to_selector,
			print_or_insert=self.Navigator.print_or_insert,
			region_set=self.region_set,
			search_direct=self.search_direct,
			search_get_results=self.search_get_results,
			search_key=self.search_key,
			search_open_results=self.Navigator.search_open_results,
			search_open_results_and_read=self.Navigator.search_open_results_and_read,
			search_site=self.search_site,
			select_option=self.Navigator.select_option_to_selector,
			site_check=self.Navigator.site_check,
			site_read=self.Navigator.site_read_time,
			send_tab=self.Navigator.send_tab,
			sugguest_login=self.Navigator.select_option_validate_to_selector,
			tab_check=self.Navigator.tab_check,
			tab_save=self.Navigator.tab_save_handler,
			tab_switch=self.Navigator.tab_switch_to_handler,
			validate_fields=self.Navigator.click_validate_fields,
			validate_print=self.Navigator.print_validate_to_selector,
		)
		
		self._actions_results = {}
		self._actions_results_by_params_key = {}
	
	@property
	def actions_result(self):
		return self._actions_results_by_params_key
	
	def action_call(self, method, args, kwargs):
		method_call = self._actions_methods.get(method)
		log(f'method_call={method}, args={args}, kwargs={kwargs}')
		if method_call is None:
			log(f'Exception method_call is None', method_call, level='warning')
			return None
		slp(2, 7)
		try:
			return method_call(*args, **kwargs)
		except Exception as ex:
			log(f'Exception', method_call, args, kwargs, ex, level='warning')
			raise ex
	
	def action_script(self, actions):
		# TODO check depercated
		if not isinstance(actions, list):
			actions = [actions]
		for method, args, kwargs in actions:
			self.action_call(method, args, kwargs)
		return
	
	@staticmethod
	def __get_param(value, params, actions_results):
		if not isinstance(value, str):
			return value
		
		# если в переменную надо какой-то конкретный элемент из значений выбрать например '@=search_get_results|1'
		query = value.split('|')
		
		indexes = None
		if len(query) == 2:
			value, indexes = query
		
		if value.startswith('$='):
			# берем значение из параметров params
			try:
				key = value[2:]
				_value = params.get(key)
			except Exception as ex:
				log(f'Exception', ex, level='warning')
				_value = None
		elif value.startswith('@='):
			# берем значение из сохраненных actions_results предыдущих методов
			try:
				key = value[2:]
				_value = actions_results.get(key)
			except Exception as ex:
				log(f'Exception', ex, level='warning')
				_value = None
		else:
			_value = value
		
		if indexes:
			_indexes = indexes.split(',')
			if len(_indexes) == 1:
				return _value[int(_indexes[0])]
		else:
			return _value
		
		_result = []
		for _index in _indexes:
			_result.append(_value[int(_index)])
		return tuple(_result)
	
	def _params_prepend(self, args, kwargs, params):
		# подготовка переменных для метода
		_args = []
		for a in args:
			_args.append(self.__get_param(a, params, self._actions_results))
		_kwargs = {}
		for k, v in kwargs.items():
			_kwargs[k] = self.__get_param(v, params, self._actions_results)
		return tuple(_args), _kwargs
	
	def action_series(self, actions, params=None):
		# TODO вставить паузы для ручного дейтсвия. надо сделать js кнопку управляющуую переменной на странице которую драйвер чекает перед каждым действием
		if params is None:
			params = {}
		try:
			for action in actions:
				log('action', action)
				try:
					if len(action) == 3:
						method, args, kwargs = action
					elif len(action) == 2:
						method, args = action
						kwargs = {}
					elif len(action) == 1:
						method = action[0]
						args = ()
						kwargs = {}
					else:
						log(f'Exception len in action = {action}', level='warning')
						continue
				except Exception as ex:
					err = f'Exception {ex} {action}'
					log(err, level='warning')
					continue
				if not isinstance(args, (list, tuple)):
					args = (args,)
				if not isinstance(kwargs, dict):
					kwargs = {}
				
				if method.startswith('~'):
					# можно пропустить метод по рандому
					if choice([True, False]):
						log('skip method', method)
						continue
					method = method[1:]
				
				if method == ':~':
					log('Choice sub chain')
					# выбрать одну из вложеных цеочек действий
					actions = choice(args)
					return self.action_series(actions, params)
				
				if method == ':':
					log('Run sub chain')
					# запустить вложеную цеочку действий
					actions = args
					return self.action_series(actions, params)
				
				args, kwargs = self._params_prepend(args, kwargs, params)
				return_key = kwargs.pop('return_key', None)
				return_value = kwargs.pop('return_value', None)
				try:
					_result = self.action_call(method, args, kwargs)
				except Exception as ex:
					err = f'Exception {ex} {action}'
					log(err, level='warning')
					_result = None
				
				if method.startswith('assert_'):
					log('method assert result', _result)
					slp(10, 15)
					_, __, _exist = method.partition('_')
					if _exist == 'exist':
						if not _result:
							break
					if _exist == 'not_exist':
						if _result:
							break
				
				if return_value is None:
					if not isinstance(_result, (str, int, float, list, tuple, set, dict)):
						return_value = str(_result)
					else:
						return_value = _result
				
				# сохраняем результат вызова функции в словарь
				if return_key is not None:
					self._actions_results_by_params_key[return_key] = return_value
					method_key = return_key
				else:
					method_key = method
				
				self._actions_results[method_key] = return_value
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
		
		return self
