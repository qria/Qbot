color_code = {'white':'00', 'black' : '01', 'blue' : '02', 'green' : '03', 'red' : '04', 'brown': '05', 'purple':'06', 'orange':'07', 'yellow':'08', 'light_green':'09', 'cyan':'10', 'light_cyan':'11', 'light_blue':'12', 'pink':'13', 'grey':'14', 'light_grey':'15'}

def white(s):
    return color('white', s)
def black(s):
    return color('black', s)
def blue(s):
    return color('blue', s)
def green(s):
    return color('green', s)
def red(s):
    return color('red', s)
def brown(s):
    return color('brown', s)
def purple(s):
    return color('purple', s)
def orange(s):
    return color('orange', s)
def yellow(s):
    return color('yellow', s)
def light_green(s):
    return color('light_green', s)
def cyan(s):
    return color('cyan', s)
def light_cyan(s):
    return color('light_cyan', s)
def light_blue(s):
    return color('light_blue', s)
def pink(s):
    return color('pink', s)
def grey(s):
    return color('grey', s)
def light_grey(s):
    return color('light_grey', s)

def color(color, s):
    """ note that this function sets later strings to black """
    return '\x03' + color_code[color] + s + '\x03'