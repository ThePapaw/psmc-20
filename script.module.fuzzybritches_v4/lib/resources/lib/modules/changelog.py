# -*- coding: utf-8 -*-
###############################################################################
#                           "A BEER-WARE LICENSE"                             #
# ----------------------------------------------------------------------------#
# Feel free to do whatever you wish with this file. Since we most likey will  #
# never meet, buy a stranger a beer. Give credit to ALL named, unnamed, past, #
# present and future dev's of this & files like this. -Share the Knowledge!   #
###############################################################################

# Addon Name: Fuzzy Britches v4
# Addon id: plugin.video.fuzzybritches_v4
# Addon Provider: The Papaw

'''
Included with the Fuzzy Britches Add-on
'''

import xbmcgui
import xbmcaddon
import os

from resources.lib.modules import control
from resources.lib.modules import log_utils


ADDON = xbmcaddon.Addon()
ADDON_INFO = ADDON.getAddonInfo
ADDON_PATH = control.transPath(ADDON_INFO('path'))
ARTADDON_PATH = xbmcaddon.Addon('script.fuzzybritches_v4.artwork').getAddonInfo('path')
MODULEADDON_PATH = xbmcaddon.Addon('script.module.fuzzybritches_v4').getAddonInfo('path')
#CHANGELOG_FILE = os.path.join(ADDON_PATH, 'changelog.txt')
CHANGELOG_FILE = os.path.join(MODULEADDON_PATH, 'changelog.txt')


TITLE = '[B]' + ADDON_INFO('name') + ' v.' + ADDON_INFO('version') + '[/B]'


def get():
    try:
        r = open(CHANGELOG_FILE)
        text = r.read()
        log_viewer(str(text))
    except Exception as e:
        log_utils.log('Exception raised in changelog: error = ' + str(e))

def log_viewer(message: str, header = ''):

    class LogViewer(xbmcgui.WindowXMLDialog):
        #key id's
        KEY_NAV_ENTER = 7
        KEY_NAV_ESC = 10
        KEY_NAV_BACK = 92

        KEY_NAV_MOVEUP = 3
        KEY_NAV_MOVEDOWN = 4
        KEY_NAV_PAGEUP = 5
        KEY_NAV_PAGEDOWN = 6

        #xml id's
        HEADER = 101
        TEXT = 102
        SCROLLBAR = 103
        CLOSEBUTTON = 201

        def onInit(self):
            HEADERTITLE = TITLE if header == '' else header
            self.getControl(self.HEADER).setLabel(HEADERTITLE)
            self.getControl(self.TEXT).setText(message)

        def onAction(self, action):
            actionID = action.getId()

            if actionID in[self.KEY_NAV_BACK, self.KEY_NAV_ENTER, self.KEY_NAV_ESC]:
                self.close()

            if actionID in [self.KEY_NAV_MOVEUP, self.KEY_NAV_PAGEUP]:
                self.getControl(self.TEXT).scroll(1)

            if actionID in [self.KEY_NAV_MOVEDOWN, self.KEY_NAV_PAGEDOWN]:
                self.getControl(self.TEXT).scroll(-1)

        def onClick(self, controlId):
            if controlId == self.CLOSEBUTTON:
                self.close()

    d = LogViewer('LogViewer.xml', ARTADDON_PATH, control.appearance(), '1080i')
    d.doModal()
    del d