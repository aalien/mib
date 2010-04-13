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
from parser import parse, IRCMsg
import config

import os
import re
import sys

class Mib:
    """ Main class which handles most of the core functionality.
    """
    def __init__(self):
        """ Initialize variables and read config.
        """
        sys.path.append('plugins')
        self.loaded_plugins = {} # plugin name : module
        self.cmd_callbacks = {} # command : set(function)
        self.privmsg_cmd_callbacks = {} # command : set(function)
        self.command_masks = {} # command : list(regexp)

        self.plugins = set(config.LOAD_PLUGINS)
        self.cmd_prefixes = set(config.CMD_PREFIXES)
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
        for plugin in self.plugins:
            print self.load_plugin(plugin)[1]

    def run(self):
        """ Start socket's main loop.
        """
        self.socket.run()

    def clean(self):
        for plugin in self.loaded_plugins.itervalues():
            plugin.clean()

    def parse_line(self, line):
        """ Parse line and call callbacks registered for command.
        """
        print line
        parsed = parse(line)
        if not parsed:
            print 'Unable to parse line: "%s"' %(line)
            return
        # call registered functions
        for function in self.cmd_callbacks.get(parsed.cmd, ()):
            try:
                function(parsed)
            except Exception, e:
                print 'Error from function', repr(function), ':', e
        # call registered privmsg functions with pre-parsed line
        if parsed.cmd == 'PRIVMSG':
            cmd_prefix = parsed.postfix.split(' ', 1)[0]
            postfix = parsed.postfix[len(cmd_prefix):].lstrip()
            if cmd_prefix in self.cmd_prefixes:
                print 'Found command prefix', cmd_prefix
                cmd = postfix.lstrip().split(' ', 1)[0]
                postfix = postfix[len(cmd):].lstrip()
                stripped_parsed = IRCMsg(parsed.prefix, parsed.cmd,
                                         parsed.params, postfix)
                print "stripped_parsed = ", stripped_parsed
                print 'Searching for command', cmd
                for function in self.privmsg_cmd_callbacks.get(cmd, ()):
                    run = False
                    if cmd not in self.command_masks:
                        run = True
                    else:
                        print 'There are limitations for this command'
                        for regexp in self.command_masks[cmd]:
                            print 'Matching %s to %s' % (parsed.prefix,
                                                         regexp.pattern)
                            if regexp.match(parsed.prefix):
                                run = True
                                break
                    if run:
                        try:
                            print 'Executing command %s' % cmd
                            function(stripped_parsed)
                        except Exception, e:
                            print 'Error from function', repr(function), ':', e

    def load_plugin(self, plugin, params=None):
        """ str, ([]) -> (bool, str)
            
            Loads plugin from plugins/<plugin>.py
            Params will be given to plugin's constructor.
            Returns a tuple with a boolean stating if the plugin
            was loaded properly and a message telling what happened.
        """
        if plugin in self.loaded_plugins:
            return (False, 'Plugin %s already loaded' %(plugin))
        if not os.path.exists(os.path.join('plugins', plugin + '.py')):
            return (False, 'Plugin %s does not exists' %(plugin))

        try:
            module = __import__(plugin)
            if params:
                obj = module.init(self, params)
            else:
                obj = module.init(self)
            success = True
        except Exception, err:
            success = False
            print err

        if success:
            self.loaded_plugins[plugin] = obj
            return (True, 'Loaded plugin %s' %(plugin))
        else:
            return (False, 'Failed to load plugin %s' %(plugin))

    def register_cmd(self, cmd, function):
        """ Registers a function to be called when a line with
            cmd is seen. Function must take one named tuple parameter.
            Tuple contains line in parsed form with fields
            (prefix, cmd, params, postfix)
        """
        self.cmd_callbacks.setdefault(cmd, set()).add(function)

    def register_privmsg_cmd(self, cmd, function):
        """ Registers a function to be called when a PRIVMSG with
            cmd is seen. Function must take one named tuple parameter.
            Tuple contains line in parsed form with fields
            (prefix, cmd, params,
            postfix stripped from one of CMD_PREFIXES and cmd)
        """
        self.privmsg_cmd_callbacks.setdefault(cmd, set()).add(function)

    def add_cmd_permission(self, cmd, mask, regexpify=True):
        """ Creates a regular expression from the mask and adds it
            to the list of allowed regexps for the cmd.
            If regexpify is false, mask will be used as is
        """
        if regexpify:
            mask = mask.replace('*', '.*').replace('?', '.?')
        m = re.compile(mask)
        self.command_masks.setdefault(cmd, []).append(m)

    def rm_cmd_permission(self, cmd, mask, regexpify=True):
        """ Creates a regular expression from the mask, and removes
            the permission for that expression from cmd's list.
            If regexpify is false, mask will be used as is
        """
        if regexpify:
            mask = mask.replace('*', '.*').replace('?', '.?')
        if cmd in self.command_masks:
            for index, regexp in enumerate(self.command_masks[cmd]):
                if regexp.pattern == mask:
                    del self.command_masks[cmd][index]
                    break

if __name__ == "__main__":
    mib = Mib()
    try:
        mib.run()
    except Exception, e:
        print 'ERROR: ', e
    except:
        pass
    mib.clean()
    print 'Quiting!'

