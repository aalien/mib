#    This file is part of mib.
#
#    mib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    mib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with mib.  If not, see <http://www.gnu.org/licenses/>.
#

import select
import socket
import sys

class IrcSocket:
    """ Class for talking with an IRC server.
    """
    def __init__(self, host, port, nick, username, realname):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.nick = nick
        self.username = username
        self.realname = realname
        self.connected = False
        self.sendqueue = []
        self.channels = set()
        self.onChannels = set()
        self.readline_cbs = set()

    def join(self, channel):
        """ Adds channel to the list of channels that should be joined
        """
        self.channels.append(channel)

    def quit(self, reason=''):
        """ Quits the session. Reason will be sent as the quit message.
        """
        if reason != '':
            reply = 'QUIT :' + msg.params + ' (' + msg.nick + ')'
        else:
            reply = 'QUIT :(' + msg.nick + ')'
        self.send(reply)

    def send(self, msg):
        """ Adds msg to the queue of messages that will be sent to server.
            msg is _not_ a PRIVMSG, but an IRC protocol message.
        """
        self.sendqueue.append(msg)

    def register_readline_cb(self, function):
        """ Registers a callback for function to call with every read line.
            Function must take one string parameter.
            Every registered function will be called once.
        """
        self.readline_cbs.add(function)

    def __readline(self):
        """ Reads line from the socket and strips the newline char(s).
            Calls registered readline callbacks with the stripped line.
            For internal use.
        """
        s = self.buffer.readline()
        if s:
            if s[-2:] == '\r\n':
                s = s[:-2]
            elif s[-1:] in '\r\n':
                s = s[:-1]
            for function in self.readline_cbs:
                function(s)
        return s

    def __connect(self):
        """ Connects the socket to the server and registers the connection.
            For internal use.
        """
        self.sock.connect((self.host, self.port))
        self.buffer = self.sock.makefile('r')
        self.send('NICK ' + self.nick)
        self.send('USER ' + self.username + ' ' +
            socket.gethostname() + ' ' + self.host + ' :' + self.realname)

    def __send(self):
        """ Sends a message from the message queue to the server.
            For internal use.
        """
        if len(self.sendqueue) != 0:
            msg = self.sendqueue.pop(0)
            print msg
            self.sock.send(msg + '\r\n')

    def __join(self):
        """ Joins the channels in the channel list.
            For internal use.
        """
        for channel in self.channels.difference(self.onChannels):
            self.send('JOIN ' + channel)
            self.onChannels.add(channel)

    def run(self):
        """ The main loop.
        """
        self.running = True
        self.__connect()
        try:
            while self.running:
                self.__send()
                inputready, _, _ = select.select([sys.stdin, self.buffer],
                                                 [], [], 0.1)
                if sys.stdin in inputready:
                    line = sys.stdin.readline()
                    if line != '':
                        self.send(line)
                if self.buffer in inputready:
                    line = self.__readline()
                    if not line:
                        self.running = False
                        continue
                    print line
                    if line.startswith('PING'):
                        self.__handleping(line)
                    if line.startswith(':%s 251' %(self.host)):
                        self.__handlelusermsg(line)
                if (self.connected and
                    not self.channels.issubset(self.onChannels)):
                    self.__join()
        except Exception, e:
            print 'ERROR: ', e
        except: # exceptions not of type Exception
            pass
        finally:
            print 'Quiting!'
            self.sock.close()

    def __handleping(self, line):
        """ Handles PING message from the server
            and answers with PONG message.
            For internal use.
        """
        pong = line.split()[1]
        reply = 'PONG ' + pong
        self.send(reply)

    def __handlelusermsg(self, line):
        """ Handles LUSERCLIENT (251) message.
            This is here because some irc servers don't react to
            messages sent before the connection is properly initialized.
            For internal use.
        """
        self.connected = True

