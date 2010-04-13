from parser import parse_prefix

class Limit_Plugin:
    """ Plugin to control which users can use which commands.
    """

    def __init__(self, mib, params=None):
        self.mib = mib
        self.mib.register_privmsg_cmd('allow', self.allow)
        self.mib.register_privmsg_cmd('deny', self.deny)
        self.load_lists()

    def clean(self):
        self.save_lists()

    def allow(self, msg):
        parsed = self.parse(msg)
        if parsed:
            cmd, mask = parsed
            print 'Adding %s for command %s' % (mask, cmd)
            self.mib.add_cmd_permission(cmd, mask)

    def deny(self, msg):
        parsed = self.parse(msg)
        if parsed:
            cmd, mask = parsed
            print 'Removing %s from command %s' % (mask, cmd)
            self.mib.rm_cmd_permission(cmd, mask)

    def parse(self, msg):
        prefix = parse_prefix(msg.prefix)
        postfix = msg.postfix.split()
        if len(postfix) != 2:
            error_msg = 'Usage: mask command'
            self.mib.socket.send('PRIVMSG %s :%s' % (prefix.nick, error_msg))
            return None
        mask = postfix[0]
        cmd = postfix[1]
        return (cmd, mask)

    def load_lists(self):
        try:
            f = open('limit.cfg')
        except IOError:
            return

        try:
            for line in f:
                line = line.split()
                if len(line) != 2:
                    continue # config file syntax error
                cmd = line[0]
                mask = line[1]
                self.mib.add_cmd_permission(cmd, mask, regexpify=False)
        finally:
            f.close()

    def save_lists(self):
        try:
            f = open('limit.cfg', 'w')
        except IOError:
            return

        try:
            for cmd in self.mib.command_masks:
                for regexp in self.mib.command_masks[cmd]:
                    line = '%s %s\n' % (cmd, regexp.pattern)
                    f.write(line)
        finally:
            f.close()

def init(mib, params=None):
    return Limit_Plugin(mib, params)

