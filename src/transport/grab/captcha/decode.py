import os

from itools.captcha.anticap import AntiCaptchaClient

from ....handlers.captcha import captcha_check_img
from ..selector import Selector
from itools.timer.tools import index_day

from ....config import log


class CaptchaDecode:
	def __init__(self, grab, anticapcha_options, proxy, routes, provider_captcha=None, selector=Selector()):
		self.grab = grab
		self.anticapcha = anticapcha_options
		self.proxy = proxy
		self.Selector = selector
		self.Routes = routes
		self.ProviderCaptcha = provider_captcha
		self.captcha_repeat = self.anticapcha['repeat']
		
		_path_captcha = os.path.join(self.anticapcha['save_path'], index_day())
		os.makedirs(os.path.dirname(_path_captcha), exist_ok=True)
		self.captcha_dir = _path_captcha
		
		self.ClientAntiCaptcha = AntiCaptchaClient(
			apikey=self.anticapcha['key'],
			sleep_time=self.anticapcha['sleep'],
			language=self.anticapcha['lang'],
			phrase=self.anticapcha['phrase'],
			case=self.anticapcha['case']
		)
	
	def _get_url_img(self):
		try:
			url = self.Selector.select(obj=self.grab.doc, selector=self.Routes.IMG, attr_name='src')
		except Exception as ex:
			log('Exception _get_answer', ex, level='warning')
			url = None
		return url
	
	def _get_answer_img(self, url):
		try:
			_grab = self.grab.clone()
		except Exception as ex:
			log('Exception', ex, level='warning')
			raise ex
		try:
			answer, captcha_file, task_id = self.ClientAntiCaptcha.get(
				captcha_url=url,
				cur_dir=self.captcha_dir,
				proxy=self.proxy,
				repeated=2,
				get_image_callback=_grab.download
			)
		except Exception as ex:
			log('Exception _get_answer', ex, level='warning')
			answer, captcha_file, task_id = None, None, None
		return answer, captcha_file, task_id
	
	def _send_answer_img(self, answer):
		try:
			self.grab.doc.set_input_by_xpath(self.Routes.INPUT, answer)
		except Exception as ex:
			log('Exception', ex, level='warning')
			return None
		try:
			self.grab.doc.set_input_by_xpath(self.Routes.INPUT, answer)
			self.grab.submit()
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
			self.ProviderCaptcha.add(result)
		return result
	
	def _captcha_check_img(self):
		return captcha_check_img(self)
