#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#**********************************************************************************
#*                                                                                *
#*                             Brave Browser The Latest                           *
#*          ------------------------------------------------------------          *
#*                                                                                *
#**********************************************************************************
#
# Copyright 2025 Antonio Leal, Porto Salvo, Portugal
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# $Id:$


#**********************************************************************************
#*                                                                                *
#*                                    Libraries                                   *
#*                                                                                *
#**********************************************************************************
import os
import subprocess
import time
import sys
import xml.etree.ElementTree as ET
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

#**********************************************************************************
#*                                                                                *
# Program variables and constants                                                 *
#*                                                                                *
#**********************************************************************************
DOWNLOAD_LINK = 'https://github.com/brave/brave-browser/releases/download/v%s/'
BINARY_FILE = 'brave-browser_%s_amd64.deb'
APP_PATH = '/opt/brave-browser-the-latest'
LASTRUN = APP_PATH + '/lastrun'
A_DAY_IN_SECONDS = 86400

MESSAGE_1 = """Hey, there is a new Brave Browser release.

Your version : %s
New version  : %s

Do you want to install it?
"""

MESSAGE_2 = """Brave is now at version %s
Please review the installation output below:
"""

MESSAGE_3 = """Brave Browser versions available:
Your version   : %s
Latest version : %s

You can now install it for the first time or, if
applicable, upgrade to the newest version.
Proceed with install or upgrade?
"""

MESSAGE_4 = """You cannot run this program while the
brave-browser from SlackBuilds.org is installed,
as both are incompatible.

If you do want to have automated updates
then please remove the brave-browser and
install it using this program.
"""

MESSAGE_5 = """Congratulations !

Your Brave Browser is already at the
latest version : %s
"""

MESSAGE_6 = """Failed to download the %s archive.

Please re-run the program
using the menu launcher.
"""

command_ok = False
command_yes = False
command_no = False
builder = None

#**********************************************************************************
#*                                                                                *
#                                  Gui Handlers                                   *
#*                                                                                *
#**********************************************************************************
class YesNoHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonYesPressed(self, ButtonYes):
        global builder, command_yes
        window = builder.get_object("yesno-dialog")
        window.hide()
        Gtk.main_quit()
        command_yes = True
    def onButtonNoPressed(self, ButtonNo):
        global builder, command_no
        window = builder.get_object("yesno-dialog")
        window.hide()
        Gtk.main_quit()
        command_no = True

class OKHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonOKPressed(self, ButtonOK):
        global builder, command_ok
        window = builder.get_object("ok-dialog")
        window.hide()
        Gtk.main_quit()
        command_ok = True

class EndHandler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    def onButtonOKPressed(self, ButtonOK):
        Gtk.main_quit()

#**********************************************************************************
#*                                                                                *
#                                    Dialogs                                      *
#*                                                                                *
#**********************************************************************************
def yesno_dialog(message):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("dialogs/yesno-dialog.glade")
    builder.connect_signals(YesNoHandler())
    window = builder.get_object("yesno-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(message)
    window.show_all()
    Gtk.main()

def ok_dialog(message):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("dialogs/ok-dialog.glade")
    builder.connect_signals(OKHandler())
    window = builder.get_object("ok-dialog")
    LabelMessage = builder.get_object("LabelMessage")
    LabelMessage.set_text(message)
    window.show_all()
    Gtk.main()

def end_dialog(latest_version, log):
    global builder
    builder = Gtk.Builder()
    builder.add_from_file("dialogs/end-dialog.glade")
    builder.connect_signals(EndHandler())
    window = builder.get_object("end-dialog")
    Log = builder.get_object("Label")
    Log.set_text(MESSAGE_2 % latest_version)
    Log = builder.get_object("Log")
    Log.get_buffer().set_text(log)
    window.show_all()
    Gtk.main()

#**********************************************************************************
#*                                                                                *
#                               Core functions                                    *
#*                                                                                *
#**********************************************************************************
# Get the latest Brave Browser version.
def get_latest_version():
    try:
        web_version= os.popen('curl -s  https://versions.brave.com/latest/release-linux-x64.version').read()
    except:
        web_version = 'undetermined'
    return web_version
    
# Check the current installed version, if there is one...
def get_current_version():
    if os.path.isfile("/opt/brave.com/brave/brave"):
        try:
            current_version = os.popen('/opt/brave.com/brave/brave --version | cut -d " " -f3 | cut -d "." -f 2-').read()
        except:
            current_version = 'not found'
    else:
        current_version = 'not found'
    return current_version

# Download the deb package
def download_deb_package(ver):
    os.chdir("SlackBuild")
    os.system('/usr/bin/wget %s/%s' % (DOWNLOAD_LINK % ver , BINARY_FILE % ver))
    result1 = subprocess.run('ar x %s 2>&1' % (BINARY_FILE % ver), capture_output=True, shell=True)
    result2 = subprocess.run('tar tvf data.tar.xz 2>&1', capture_output=True, shell=True)
    subprocess.run('rm -rf data.tar.xz control.tar.xz debian-binary', capture_output=False, shell=True)
    os.chdir("..")
    if (result1.returncode != 0) or (result2.returncode != 0):
        ok_dialog(MESSAGE_6 % BINARY_FILE % ver)
        delete_deb_package()
        exit(0)

# Prepare a SlackBuild and Install on you box
def install(latest_version):
    os.chdir("SlackBuild")
    log = "Installing Brave Browser " + str(latest_version)
    log = os.popen('sed  "s/_version_/%s/" brave-browser.SlackBuildTemplate > brave-browser.SlackBuild' % latest_version).read()
    log = os.popen('chmod +x brave-browser.SlackBuild').read()
    log = os.popen('./brave-browser.SlackBuild').read()
    log += os.popen('/sbin/upgradepkg --install-new /tmp/brave-browser-%s-x86_64-1.tgz' % latest_version).read()
    os.chdir("..")
    return log

# remove binary file
def delete_deb_package():
    os.chdir("SlackBuild")
    os.system('rm -rf *.deb')
    os.chdir("..")
    pass

#**********************************************************************************
#*                                                                                *
#                                Main Function                                    *
#*                                                                                *
#**********************************************************************************
def main():
    global command_yes, command_no, command_no
    os.chdir(APP_PATH)

    # Check if you are root
    if os.geteuid() != 0:
        msg='You must run this script as root.'
        print(msg)
        ok_dialog(msg)
        exit(0)

    # Only run if brave-browser from SlackBuilds.org is *not* installed
    slackbuild_version = os.popen('ls -1 /var/log/packages/brave-browser*_SBo  2> /dev/null | grep -v "the-latest"').read().strip()
    if slackbuild_version != "":
        print(MESSAGE_4)
        ok_dialog(MESSAGE_4)
        exit(0)

    # Read program arguments
    param_silent = False
    param_install_or_upgrade = False
    param_show_gui = False
    for a in sys.argv:
        if 'GUI' == a.upper():
            param_show_gui = True
        if 'INSTALL' == a.upper() or 'UPGRADE' == a.upper() or 'UPDATE' == a.upper():
            param_install_or_upgrade = True
        if 'SILENT' == a.upper():
            param_silent = True

    # Exit if $DISPLAY is not set
    if len(os.popen("echo $DISPLAY").read().strip()) == 0 and not param_silent:
        print('In order to run you must have an XServer running, otherwise use the "silent" program argument.')
        exit(0)

    # Only run once a day, even though we set cron.hourly
    if os.path.exists(LASTRUN) and not (param_install_or_upgrade or param_show_gui):
        ti_m = os.path.getmtime(LASTRUN)
        ti_n = time.time()
        if (ti_n - ti_m) < A_DAY_IN_SECONDS:
            exit(0)
    os.system('touch %s' % LASTRUN)

    current_version = str(get_current_version()).strip()
    latest_version = str(get_latest_version()).strip()

    if param_show_gui:
        if current_version != latest_version:
            yesno_dialog(MESSAGE_3 % (current_version, latest_version))
            if command_yes:
                download_deb_package(latest_version)
                log = install(latest_version)
                end_dialog(latest_version, log)
            delete_deb_package()
        else:
            ok_dialog(MESSAGE_5 % latest_version)
    else:
        if current_version != latest_version or param_install_or_upgrade:
            if not param_silent:
                yesno_dialog(MESSAGE_1 % (current_version, latest_version))
            else:
                command_yes = True
            if command_yes:
                download_deb_package(latest_version)
                log = install(latest_version)
                if not param_silent:
                    end_dialog(latest_version, log)
            delete_deb_package()

if __name__ == '__main__':
    main()

