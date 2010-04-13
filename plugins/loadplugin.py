from parser import parse_prefix

class Load_Plugin:
    """ Plugin to load plugins with a command from IRC.
    """

    def __init__(self, mib, params=None):
        self.mib = mib
        self.mib.register_privmsg_cmd('plugin', self.load_plugin)

    def clean(self):
        pass

    def load_plugin(self, msg):
        prefix = parse_prefix(msg.prefix)
        plugin = msg.postfix.split()
        if len(plugin) < 1:
            error_msg = 'Not enough parameters'
            self.mib.socket.send('PRIVMSG %s :%s' % (prefix.nick, error_msg))
            return
        if len(plugin) >= 2:
            params = plugin[1:]
        else:
            params = None
        plugin = plugin[0]
        succ, msg = self.mib.load_plugin(plugin, params)
        self.mib.socket.send('PRIVMSG %s :%s' % (prefix.nick, msg))

def init(mib, params=None):
    return Load_Plugin(mib, params)

