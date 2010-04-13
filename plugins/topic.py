from parser import parse_prefix

class Topic:
    """ Example plugin to change channels topic.
    """
    def __init__(self, mib, params=None):
        """ Constructor.
            Parameters:
                mib: Reference to mib instance
                params: List of parameters. Not used in this plugin
        """
        self.mib = mib
        self.mib.register_privmsg_cmd('topic', self.change_topic)

    def clean(self):
        pass

    def change_topic(self, msg):
        """ Changes topic according to what is given in msg
            Parameters:
                msg: IRCMsg named tuple
        """
        # channel on which to change to topic
        channel = msg.params
        sender = channel
        if channel[0] != '#':
            # private message, check for channel in the message
            # change sender to the private message sender instead of channel
            sender = parse_prefix(msg.prefix).nick
            if msg.postfix[0] != '#':
                # no channel in the message, reply with error
                self.mib.socket.send('PRIVMSG %s :%s' %(sender, 
                                                        'No channel given'))
                return
            else:
                # the channel was given as the first parameter
                channel = msg.postfix.split()[0]
                # there might be no new topic given,
                # so we must parse it separately
                # (not with channel, topic = postfix.split(' ', 1))
                topic = msg.postfix[len(channel):].lstrip()
        else:
            # message was from a channel, topic == message
            topic = msg.postfix

        if not topic:
            # topic is empty, reply with error
            self.mib.socket.send('PRIVMSG %s :%s' %(sender,
                                                    'No topic given'))
            return

        # else, we can set a new topic
        self.mib.socket.send('TOPIC %s :%s' %(channel, topic))

def init(mib, params=None):
    """ Initializer function for plugin loader. Must be named init.
        Creates a topic object and returns it to the plugin loader function.
    """
    return Topic(mib, params)

