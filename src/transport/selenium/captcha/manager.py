from .google.decode import CaptchaDecodeGoogle
from .yandex.decode import CaptchaDecodeYandex


# TODO сделать менеджер
class CaptchaManager:
	def __init__(self, search='yandex'):
		self.search = search
		self.anticaptcha_map = dict(
			yandex=CaptchaDecodeYandex,
			google=CaptchaDecodeGoogle
		)
	
	def get(self):
		anticaptcha_class: CaptchaDecodeYandex or CaptchaDecodeGoogle = self.anticaptcha_map.get(self.search, self.anticaptcha_map.get('yandex'))
		return anticaptcha_class
