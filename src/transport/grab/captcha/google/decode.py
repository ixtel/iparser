from .constants import CaptchaRoutesGoogle
from ..decode import CaptchaDecode
from ...selector import Selector


class CaptchaDecodeGoogle(CaptchaDecode):
	def __init__(self, grab, anticapcha_options, proxy, provider_captcha=None, selector=Selector()):
		super().__init__(
			grab=grab,
			anticapcha_options=anticapcha_options,
			proxy=proxy,
			routes=CaptchaRoutesGoogle,
			provider_captcha=provider_captcha,
			selector=selector
		)
