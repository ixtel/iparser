from .constants import CaptchaRoutesGoogle
from ..decode import CaptchaDecode
from ...navigator import Navigator


class CaptchaDecodeGoogle(CaptchaDecode):
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
			routes=CaptchaRoutesGoogle,
			provider_captcha=provider_captcha,
		)
