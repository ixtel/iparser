import time

from .constants import CaptchaRoutesYandex
from ..decode import CaptchaDecode
from ...navigator import Navigator
from ...config import log


class CaptchaDecodeYandex(CaptchaDecode):
	def __init__(
			self,
			navigator: Navigator,
			anticapcha_options: dict,
			proxy: dict,
			provider_captcha=None,
	):
		super().__init__(
			navigator=navigator,
			anticapcha_options=anticapcha_options,
			proxy=proxy,
			routes=CaptchaRoutesYandex,
			provider_captcha=provider_captcha,
		)
	
	def _captcha_check_smart(self):
		try:
			check = self.Navigator.get_element(self.Routes.SMART, wait=2)
			if check:
				self._proxy_handler(self.proxy.get('ip'))
				self.Navigator.click_to_selector(self.Routes.SMART, wait=2)
				time.sleep(3)
				log('Have Smart Captcha')
			if not self.Navigator.get_element(self.Routes.SMART, wait=2):
				return True
			return False
		except Exception as ex:
			log('Exception', ex, level='warning')
			return False
