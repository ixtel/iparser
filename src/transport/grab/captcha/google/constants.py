class CaptchaRoutesGoogle(object):
	SMART = [
		'//span[@id="recaptcha-anchor"]',
		'//div[@id="recaptcha-checkbox-border"]',
	]
	IMG = [
		'//div[@id="rc-imageselect"]',
	]
	IMG_HEAD = [
		'//div[@class="rc-imageselect-desc-wrapper"]/strong'
	]
	INPUT = [
	]
	SEND = [
		'//button[@id="recaptcha-verify-button"]',
	]
