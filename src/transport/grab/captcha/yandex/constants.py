class CaptchaRoutesYandex(object):
	SMART = '//input[@class="CheckboxCaptcha-Button"]'
	IMG = [
		'//img[@class="form__captcha"]',
		'//img[@class="captcha__image"]',
		'//img[@class="AdvancedCaptcha-Image"]',
	]
	IMG_ERROR = [
		'//*[@class="captcha-wrapper"]/*[@class="field__error"]'
	]
	IMG_HEAD = [
	]
	INPUT = [
		'//input[@id="rep"]',
		'//input[@id="captcha"]',
	]
	SEND = [
		'//form/*/button[@class="form__submit"]',
		'//*[@class="form__submit"]',
	]
