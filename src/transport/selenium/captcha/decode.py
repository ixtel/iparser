import os

from itools.captcha.anticap import get_client
from itools.timer.tools import index_day

from ..config import log
from ....handlers.captcha import captcha_check_img
from ..navigator import Navigator


class CaptchaDecode:
	def __init__(
			self,
			navigator: Navigator,
			anticapcha_options: dict,
			proxy: dict,
			routes,
			provider_captcha=None,
	):
		self.Navigator = navigator
		self.anticapcha_options = anticapcha_options
		if proxy is None:
			proxy = {}
		self.proxy = proxy
		self.Routes = routes
		
		# колбэк для сохранения результата
		self.ProviderCaptcha = provider_captcha
		
		self._captcha_repeat = self.anticapcha_options.pop('repeat', 3)
		self._captcha_service = self.anticapcha_options.pop('service', 'rucaptcha')
		self._proxy_handler = self.anticapcha_options.pop('proxy_handler', lambda x: None)
		
		_path_captcha = os.path.join(self.anticapcha_options['save_path'], index_day())
		os.makedirs(os.path.dirname(_path_captcha), exist_ok=True)
		self._captcha_dir = _path_captcha
		log('anticapcha_options', anticapcha_options)
		self.ClientAntiCaptcha = get_client(self._captcha_service)(
			apikey=self.anticapcha_options['key'],
			sleep_time=self.anticapcha_options['sleep'],
			language=self.anticapcha_options['lang'],
			phrase=self.anticapcha_options['phrase'],
			regsense=self.anticapcha_options['regsense']
		)
	
	def _get_url_img(self):
		try:
			url = self.Navigator.get_element(selector=self.Routes.IMG, attr_name='src', wait=2)
			if url:
				self._proxy_handler(self.proxy.get('ip'))
		except Exception as ex:
			log('Exception _get_url_img', ex, level='warning')
			url = None
		return url
	
	def _get_answer_img(self, url):
		cookies = self.Navigator.get_cookies_object()
		log('cookies', cookies)
		try:
			answer, captcha_file, task_id = self.ClientAntiCaptcha.get(
				captcha_url=url,
				cur_dir=self._captcha_dir,
				proxy=self.proxy,
				repeated=2,
				get_image_callback=None,
				cookies=cookies,
			)
		except Exception as ex:
			log('Exception _get_answer', ex, level='warning')
			answer, captcha_file, task_id = None, None, None
		return answer, captcha_file, task_id
	
	def _send_answer_img(self, answer):
		try:
			self.Navigator.print_to_selector(self.Routes.INPUT, answer, wait=2)
		except Exception as ex:
			log('Exception', ex, level='warning')
			# Если нет инпута для ввода значит уже каптча введена
			return None
		try:
			self.Navigator.click_to_selector(self.Routes.SEND, wait=2)
			return True
		except Exception as ex:
			log('Exception', ex, level='warning')
			return False
	
	def _send_report_img(self, task_id):
		return self.ClientAntiCaptcha.send_report(task_id)
	
	def _save_answer_img(self, answer, captcha_file, recognized=1):
		result = {
			'captcha': captcha_file,
			'answer': answer,
			'recognized': recognized,
		}
		if self.ProviderCaptcha is not None:
			# TODO self.ProviderCaptcha.add
			try:
				self.ProviderCaptcha.add(result)
			except Exception as ex:
				log(f'Exception', ex, level='warning')
				pass
		return result
	
	def _captcha_check_smart(self):
		pass
	
	def captcha_check(self):
		return self._captcha_check_smart() and captcha_check_img(self)


class CaptchaDecodePassed:
	def __init__(self, *args, **kwargs):
		pass
	
	def __getattr__(self, item):
		def _pass(*_, **__):
			return False
		
		return _pass
