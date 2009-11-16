#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# mib: Modular irc bot
# Copyright Antti Laine <antti.a.laine@tut.fi>
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from ircsocket import IrcSocket
from parser import parse
import config

import sys

class Mib:
    """ Main class which handles most of the core functionality.
    """
    def __init__(self):
        """ Initialize variables and read config.
        """
        sys.path.append('plugins')
        self.loadedPlugins = {} # plugin name : module
        self.cmd_callbacks = {} # command : set(function)

        self.nick = config.NICK
        self.username = config.USERNAME
        self.realname = config.REALNAME
        self.server, self.port = config.SERVER
        self.channels = config.CHANNELS
        self.socket = IrcSocket(self.server, self.port, self.nick,
                                self.username, self.realname)
        self.socket.register_readline_cb(self.parse_line)
        for channel in self.channels:
            self.socket.join(channel)

    def run(self):
        """ Start socket's main loop.
        """
        self.socket.run()

    def parse_line(self, line):
        """ Parse line and call callback registered for command.
        """
        print line
        parsed = parse(line)
        if not parsed:
            print 'Unable to parse line: "%s"' %(line)
            return
        for function in self.cmd_callbacks.get(parsed.cmd, ()):
            function(parsed)

    def loadPlugin(self, plugin, params=None):
        """ str, ([]) -> (bool, str)
            
            Loads plugin from plugins/<plugin>.py
            Params will be given to plugin's constructor.
            Returns a tuple with a boolean stating if the plugin
            was loaded properly and a message telling what happened.
        """
        if plugin in self.loadedPlugins:
            return (False, 'Plugin %s already loaded' %(plugin))
        if not os.path.exists(os.path.join('plugins', plugin + '.py')):
            return (False, 'Plugin %s does not exists' %(plugin))

        try:
            exec('from %s import %s' %(plugin, plugin))
            if params:
                exec('obj = %s(self, params)' %(plugin))
            else:
                exec('obj = %s(self)' %(plugin))
            success = True
        except Exception, err:
            success = False
            print err

        if success:
            self.loadedPlugins[plugin] = obj
            return (True, 'Loaded plugin %s' %(plugin))
        else:
            return (False, 'Failed to load plugin %s' %(plugin))

    def unloadPlugin(self, plugin):
        """ str -> (bool, str)
            
            Unloads <plugin> if it's loaded.
            Return a tuple with a boolean stating if the plugin
            was unloaded properly and a message telling what happened.
        """
        if plugin in self.loadedPlugins:
            try:
                exec('del %s' %(plugin))
                sys.modules.pop(plugin)
                success = True
            except Exception, err:
                success = False
                print err
        else:
            success = False
        if success:
            del self.loadedPlugins[plugin]
            return (True, 'Unloaded plugin %s' %(plugin))
        else:
            return (False, 'Failed to unload plugin %s' %(plugin))

    def register_cmd(self, cmd, function):
        """ Registers a function to be called when a line with
            cmd is seen. Function must take one named tuple parameter.
            Tuple contains line in parsed form with fields
            (sender, nick, user, host), command, to, channel, message
        """
        self.cmd_callbacks.setdefault(cmd, set()).add(function)

if __name__ == "__main__":
    mib = Mib()
    try:
        mib.run()
    except Exception, e:
        print 'ERROR: ', e
    except:
        pass
    print 'Quiting!'

