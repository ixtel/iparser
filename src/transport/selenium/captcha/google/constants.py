class CaptchaRoutesGoogle(object):
	SMART = [
		'span[id="recaptcha-anchor"]',
		'div[id="recaptcha-checkbox-border"]',
	]
	
	SMART_BAN = [
		'.rc-doscaptcha-header',
	]
	
	IMG = [
		'div[id="rc-imageselect"]',
	]
	
	IMG_ERROR = []
	
	IMG_HEAD = [
		'div.rc-imageselect-desc-wrapper strong',
	]
	
	INPUT = []
	
	SEND = [
		'button[id="recaptcha-verify-button"]',
	]
	
	RELOAD = [
		'button[id="recaptcha-reload-button"]',
	]
