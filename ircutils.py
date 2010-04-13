""" Collection of helper functions
"""

def privmsg(to, msg):
    return 'PRIVMSG %s :%s' % (to, msg)

def join(channel):
    return 'JOIN %s' % channel

def leave(channel, reason=''):
    return 'PART %s :%s' % (channel, reason)

def quit(reason=''):
    return 'QUIT :%s' % reason

def topic(channel, topic=''):
    if topic:
        return 'TOPIC %s :%s' % (channel, topic)
    else:
        return 'TOPIC %s' % channel

def mode(mode, target):
    target = target.split()
    if len(target) != 0:
        return 'MODE %s %s' % (len(target) * mode, ' '.join(target))
    else:
        return 'MODE %s' % target

def op(users):
    return mode('+o', users)

def deop(users):
    return mode('-o', users)

def voice(users):
    return mode('+v', users)

def devoice(users):
    return mode('-v', users)

def ban(mask):
    return mode('+b', mask)

def unban(mask):
    return mode('-b', mask)

