import base64
import os
import sys
import time
import zipfile
from random import choice
from random import randint

from itools.network.tools import get_domain_from_url
from itools.timer.tools import slp
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import *
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from userface import agent

from .config import CONF, log, iloger

__all__ = ('Driver',)


def chrome_proxy_ext_build(proxy_host, proxy_port, proxy_user, proxy_pass):
	print(proxy_host, proxy_port, proxy_user, proxy_pass)
	
	manifest_json = """
		{
			"version": "1.0.0",
			"manifest_version": 2,
			"name": "Chrome Proxy",
			"permissions": [
				"proxy",
				"tabs",
				"unlimitedStorage",
				"storage",
				"background",
				"cookies",
				"desktopCapture",
				"displaySource",
				"<all_urls>",
				"webRequest",
				"webRequestBlocking"
			],
			"background": {
				"scripts": ["background.js"]
			},
			"minimum_chrome_version":"22.0.0"
		}
		"""
	
	background_js = """
	var config = {
		mode: "fixed_servers",
		rules: {
			singleProxy: {
				scheme: "http",
				host: "%(host)s",
				port: parseInt(%(port)d)
			},
		bypassList: ["foobar.com"]
		}
	};
	chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
	function callbackFn(details) {
		return {
			authCredentials: {
				username: "%(user)s",
				password: "%(pass)s"
			}
		};
	}
	chrome.webRequest.onAuthRequired.addListener(
				callbackFn,
				{urls: ["<all_urls>"]},
				['blocking']
	);
	""" % {
		"host": str(proxy_host),
		"port": int(proxy_port),
		"user": str(proxy_user),
		"pass": str(proxy_pass),
	}
	
	pluginfile = './tmp/proxy_auth_%s_%s.zip' % (str(int(time.time())), str(randint(10, 90)))
	
	with zipfile.ZipFile(pluginfile, 'w') as zp:
		zp.writestr("manifest.json", manifest_json)
		zp.writestr("background.js", background_js)
	
	return pluginfile


class Driver:
	def __init__(self, user_agent=False, resolute=False, proxy=None, proxy_auth=None, cookies=None, target_url=None):
		if target_url is None:
			target_url = []
		if not isinstance(target_url, (list, tuple)):
			target_url = [target_url]
		if proxy_auth is None:
			proxy_auth = {'user': '', 'pass': ''}
		
		iloger.set_level('INFO')
		self.cookies = cookies
		resolutes = [
			'1920x1080',
			'1366x768',
			'1280x1024',
			'1280x800',
			'1024x768',
		]
		self.user_agent = user_agent if user_agent else agent.Agent().user_agent()
		res_str = choice(resolutes).split('x')
		self.resolute = resolute.split('x') if isinstance(resolute, str) and len(resolute) else resolute if isinstance(resolute, list) else res_str
		
		self.proxy = proxy
		self.proxy_auth = proxy_auth
		self.window_width = self.resolute[0]
		self.window_height = self.resolute[1]
		self._url_allow = ''
		for _target_url in target_url:
			if _target_url:
				_target_domain = get_domain_from_url(_target_url)
				self._url_allow += f'{_target_domain} http://{_target_domain} https://{_target_domain} '
	
	def browser(self, name='firefox'):
		_driver = getattr(self, name)()
		_driver.set_page_load_timeout(int(CONF.TIMEOUT_PAGE_LOAD))
		_driver.set_script_timeout(int(CONF.TIMEOUT_SET_SCRIPT))
		return _driver
	
	def chrome(self):
		options = webdriver.ChromeOptions()
		options.add_argument('--ignore-certificate-errors')
		options.add_argument("user-agent=%s" % str(self.user_agent))
		options.add_argument("--disable-internal-flash")
		options.add_argument("--disable-plugins-discovery")
		options.add_argument("--disable-bundled-ppapi-flash")
		options.add_argument("--disable-infobars")
		options.add_argument("window-size=%s,%s" % (self.window_width, self.window_height))
		
		proxy_ip = self.proxy.split(':')[0]
		proxy_port = self.proxy.split(':')[1]
		pluginfile = chrome_proxy_ext_build(proxy_ip, proxy_port, self.proxy_auth['user'], self.proxy_auth['pass'])
		slp(2)
		
		project_root = os.path.dirname(os.path.abspath(__file__))
		extension_root = os.path.join(project_root, pluginfile)
		
		options.add_extension(extension_root)
		mobile_emulation = {
			"deviceMetrics": {"width": int(self.window_width), "height": int(self.window_height), "pixelRatio": 1.0, "touch": False},
			"userAgent": str(self.user_agent)
		}
		options.add_experimental_option("mobileEmulation", mobile_emulation)
		
		pref = {"plugins.plugins_disabled": ["Adobe Flash Player", "Shockwave Flash"], "profile.default_content_setting_values.geolocation": 2}
		options.add_experimental_option("prefs", pref)
		executable_path = "c:/mytools/chromedriver.exe"
		_driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
		_driver.set_window_size(self.window_width, self.window_height)
		return _driver
	
	def _firefox_profile(self):
		profile = FirefoxProfile(CONF.FIREFOX_PROFILE)
		profile.accept_untrusted_certs = True
		profile.set_preference('browser.shell.checkDefaultBrowser', False)
		profile.set_preference('browser.startup.page', 0)
		profile.set_preference('dom.ipc.plugins.enabled.timeoutSecs', 15)
		profile.set_preference('dom.max_script_run_time', 10)
		profile.set_preference('extensions.checkCompatibility', False)
		profile.set_preference('extensions.checkUpdateSecurity', False)
		profile.set_preference('extensions.update.autoUpdateEnabled', False)
		profile.set_preference('extensions.update.enabled', False)
		profile.set_preference('network.http.max-connections-per-server', 30)
		profile.set_preference('network.prefetch-next', False)
		profile.set_preference('toolkit.storage.synchronous', 0)
		profile.set_preference('image.animation_mode', 'none')
		profile.set_preference('images.dither', False)
		profile.set_preference('content.notify.interval', 1000000)
		profile.set_preference('content.switch.treshold', 100000)
		profile.set_preference('nglayout.initialpaint.delay', 1000000)
		profile.set_preference('network.dnscacheentries', 200)
		profile.set_preference('network.dnscacheexpiration', 600)
		profile.set_preference("general.useragent.override", str(self.user_agent))
		profile.set_preference('browser.download.folderList', 2)  # custom location
		profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
		profile.set_preference("browser.download.manager.closeWhenDone", True)
		profile.set_preference("network.http.connection-timeout", 15)
		profile.set_preference("network.http.connection-retry-timeout", 15)
		profile.set_preference("http.response.timeout", 5)
		profile.set_preference("dom.max_script_run_time", 5)
		profile.set_preference("browser.download.manager.focusWhenStarting", False)
		profile.set_preference('browser.download.manager.showWhenStarting', False)
		profile.set_preference('browser.download.dir', 'C:/tmp')
		profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
		profile.set_preference(
			'browser.helperApps.neverAsk.saveToDisk',
			"application/x-zip; "
			"application/x-zip-compressed; "
			"application/octet-stream; "
			"application/zip; "
			"application/x-msdownload",
		)
		profile.set_preference("browser.link.open_newwindow", 3)
		profile.set_preference("browser.link.open_external", 1)
		profile.set_preference("security.fileuri.strict_origin_policy", False)
		profile.set_preference(
			"capability.policy.maonoscript.sites",
			self._url_allow +
			"ajax.googleapis.com bootstrapcdn.com code.jquery.com google-analytics.com google.com google.ru googletagmanager.com gstatic.com "
			"nflxext.com yandex.net yandex.ru yandex.site yastatic.net [System+Principal] about: about:addons about:blank about:blocked "
			"about:certerror about:config about:crashes about:feeds about:home about:memory about:neterror about:plugins about:pocket-saved "
			"about:pocket-signup about:preferences about:privatebrowsing about:sessionrestore about:srcdoc about:support about:tabcrashed blob: "
			"chrome: http://bootstrapcdn.com http://google-analytics.com http://google.com https://google.com http://google.ru https://google.ru "
			"http://googletagmanager.com http://gstatic.com http://nflxext.com http://yandex.net http://yandex.ru http://yandex.site "
			"http://yastatic.net https://bootstrapcdn.com https://google-analytics.com https://google.com https://googletagmanager.com "
			"https://gstatic.com https://nflxext.com https://yandex.net https://yandex.ru https://yandex.site https://yastatic.net mediasource: "
			"moz-extension: moz-safe-about: resource: "
		)
		return profile
	
	def firefox(self):
		log('CONF.FIREFOX_PROFILE', CONF.FIREFOX_PROFILE)
		profile = self._firefox_profile()
		profile.update_preferences()
		if self.cookies:
			profile.set_preference('extensions.cookies-proper@robodroid.cookies', self.cookies)
		
		firefox_capabilities = DesiredCapabilities.FIREFOX
		firefox_capabilities['marionette'] = False
		binary = FirefoxBinary(CONF.FIREFOX_BINARY, log_file=sys.stdout)
		
		if self.proxy:
			if self.proxy['typ'] == 'http':
				http_proxy = ssl_proxy = "{ip}:{port}".format(**self.proxy)
				proxy = Proxy({
					'proxyType': ProxyType.MANUAL,
					'httpProxy': http_proxy,
					'sslProxy': ssl_proxy,
					'noProxy': ''})
			elif self.proxy['typ'] == 'socks':
				socks_proxy = "{ip}:{port}".format(**self.proxy)
				proxy = Proxy({
					'proxyType': ProxyType.MANUAL,
					'socksProxy': socks_proxy,
					'noProxy': ''})
			else:
				proxy = Proxy({
					'proxyType': ProxyType.DIRECT,
				})
			if self.proxy.get('login') and self.proxy.get('pas'):
				p_auth = "{login}:{pas}".format(**self.proxy)
				log('p_auth', p_auth)
				authtoken = base64.b64encode(p_auth.encode('ascii')).decode('utf-8')
				profile.set_preference('extensions.closeproxyauth.authtoken', authtoken)
			
			pass
		
		else:
			proxy = None
		
		try:
			_driver = webdriver.Firefox(
				firefox_binary=binary, firefox_profile=profile, capabilities=firefox_capabilities,
				proxy=proxy
			)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			_driver = None
			pass
		
		log('_driver', _driver)
		_driver.set_window_size(self.window_width, self.window_height)
		_driver.set_window_position(0, 0)
		return _driver
	
	def gecko(self):
		profile = self._firefox_profile()
		
		if self.cookies:
			profile.set_preference('extensions.cookies-proper@robodroid.cookies', self.cookies)
		
		firefox_capabilities = DesiredCapabilities.FIREFOX
		firefox_capabilities['marionette'] = CONF.MARIONETTE
		
		binary = FirefoxBinary(CONF.FIREFOX_BINARY, log_file=sys.stdout)
		
		options = Options()
		options.headless = CONF.HEADLESS
		
		if self.proxy:
			if self.proxy['typ'] == 'http':
				profile.set_preference("network.proxy.type", 1)  # Proxy.ProxyType.MANUAL ordinal value
				profile.set_preference("network.proxy.http", self.proxy['ip'])
				profile.set_preference("network.proxy.http_port", self.proxy['port'])
				profile.set_preference("network.proxy.ssl", self.proxy['ip'])
				profile.set_preference("network.proxy.ssl_port", self.proxy['port'])
			elif self.proxy['typ'] == 'socks':
				profile.set_preference("network.proxy.type", 1)  # Proxy.ProxyType.MANUAL ordinal value
				profile.set_preference("network.proxy.socks", self.proxy['ip'])
				profile.set_preference("network.proxy.socks_port", self.proxy['port'])
			else:
				profile.set_preference("network.proxy.type", 0)  # Proxy.ProxyType.MANUAL ordinal value
			
			p_auth = "{login}:{pas}".format(**self.proxy)
			authtoken = base64.b64encode(p_auth.encode('ascii')).decode('utf-8')
			profile.set_preference('extensions.closeproxyauth.authtoken', authtoken)
		
		profile.update_preferences()
		_driver = webdriver.Firefox(
			firefox_binary=binary,
			executable_path=CONF.FIREFOX_DRIVER,
			firefox_profile=profile,
			capabilities=firefox_capabilities,
			options=options
		)
		
		log('set_window_size', self.window_width, self.window_height)
		_driver.set_window_size(self.window_width, self.window_height)
		_driver.set_window_position(0, 0)
		return _driver
