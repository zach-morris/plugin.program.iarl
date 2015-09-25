import xbmcaddon, xbmcgui

addon = xbmcaddon.Addon(id='plugin.program.iarl')
current_setting = addon.getSetting('iarl_setting_clear_cache_value')

if 'false'.lower() in current_setting.lower():
	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Are you sure you want to clear IARL cache?', ['No','Yes'])

	if ret1 == 0:
		pass
	else:
		addon.setSetting(id='iarl_setting_clear_cache_value',value='true')
		ok_ret = current_dialog.ok('Complete','The cache was cleared.')
		print 'IARL:  Cache setting set to true'