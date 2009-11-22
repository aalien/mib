from collections import namedtuple

IRCMsg = namedtuple('IRCMsg', 'prefix cmd params postfix')

def parse(line):
    """ Parses line and returns a named tuple IRCMsg
        with fields (prefix, cmd, params, postfix).
        - prefix is the first part starting with : (colon), without the :
        - cmd is the command
        - params are the parameters for the command,
          not including the possible postfix
        - postfix is the part of the parameters starting with :, without the :
    """
    if not line:
        return None
    prefix = ''
    command = ''
    params = ''
    postfix = ''

    # prefix is present is line starts with ':'
    if line[0] == ':':
        prefix, line = line.split(' ', 1)
    
    # there might be more than one space between
    # the possible prefix and command, so we'll strip them
    command, line = line.lstrip().split(' ', 1)
    
    # postfix is present is line has ':'
    index = line.find(':')
    if index != -1:
        params = line[:index]
        postfix = line[index:]
    else:
        params = line

    # command must be non-empty
    if len(command) == 0:
        return None

    return IRCMsg(prefix=prefix[1:], cmd=command, params=params,
                  postfix=postfix[1:])

