# -*- coding: utf-8 -*-
# Todo : make a deployer to restart

import socket
from time import sleep
import datetime  # for greetings

import bs4
import requests
import re

from color import red

# constants

host, port = "ara.maa.jp", 6665

debug = True  # enables logging and stuff
local = False  # for local debugging
test = True

default_encoding = "utf-8"
jp_encoding = "ISO-2022-JP"

nick, user, realname = 'Qbot', 'Qbot', "Bot no Qria"
if test:
    nick = 'QbotDev'
master = "Qria"

puyo_channel = '#BPuyo'

command_character = ''

line_limit = 400

message_delay = 0

# program control variables init

read_buffer = ""
reload = False

# irc functions


def log(*args, **kwargs):
    # for future logings
    print(*args, **kwargs)


def send(irc_command, irc_irc_parameters, encoding=jp_encoding, prefix=None, logging=debug):
    # irc_parameters can be a single string, and this function will detect it and react accordingly.
    message = ""
    if prefix:  # using prefix in client is not advised
        message += ':' + prefix + ' '
    message += irc_command + ' '
    if isinstance(irc_irc_parameters, str):
        message += irc_irc_parameters + ' '
    else:
        message += ' '.join(irc_irc_parameters)
    message += '\r\n'
    if logging:
        log(message)
    s.send(bytes(message, encoding))


def parse(line):
    irc_parameters = line.split()
    if irc_parameters[0].startswith(':'):
        prefix = irc_parameters.pop(0)
    else:
        prefix = None
    irc_command = irc_parameters.pop(0)
    return irc_command, irc_parameters, prefix


def say(to, messages, encoding=jp_encoding):
    if isinstance(messages, list):
        say(to, '\n'.join(messages), encoding)
        return
    for message in messages.split('\n'):
        if len(message)>line_limit:
            print('WARNING : line_limit exceeded!') # only warning for now
        if local:
            print(message)
            continue
        send('PRIVMSG', (to, ':' + message), encoding)
        sleep(message_delay)


def pong(reply):
    send('PONG', reply)



# get rank
def get_soup(url):
    r = requests.get(url)
    r.encoding = 'sjis'
    text = re.sub(r'</td>[\s\r\n]*</td>','</td>', r.text)
    return bs4.BeautifulSoup(text)

def get_rank(name):
    url = 'http://www53.atpages.jp/hiroigoshima/bpuyo/rank/RankList_all.html'
    soup = get_soup(url)
    titles = soup.findAll('font', attrs={'size':'5'})
    tables = [title.find_next_sibling('table') for title in titles]

    rank = dict()
    points = dict()
    for title, table in zip(titles, tables):
        for tr in table.findAll('tr'):
            if tr.find('td'):
                nickname = tr.find('td').text
                rank[nickname] = title.text
                if len(tr.findAll('td')) > 2:
                    points[nickname] = tr.findAll('td')[2].text
                else:
                    points[nickname] = 0 # for nosi san only


    if name not in rank:
        return '無し'
    return rank[name] + ' ' + points[name] + '点'

def parse_puyo(rensa_string):
    rensas = rensa_string.split('-')
    rensas = [rensa.split('/') for rensa in rensas]
    rensas = [[c.split('&') for c in rensa] for rensa in rensas]
    rensas = [[[int(n) for n in c] for c in rensa] for rensa in rensas]
    return rensas

def jama_representation(jama_count):
    if jama_count > 1080:
        return red('●●●●●●')
    small = jama_count % 6
    big = (jama_count % 30) // 6
    gem = (jama_count % 180) // 30
    return red('●'* gem) + '◎'* big + 'o' * small

def get_score(rensas):
    score = 0
    for n, rensa in enumerate(rensas):
        rensa_count = n+1
        total_popped = sum( sum(c) for c in rensa)
        print('total_popped :', total_popped)
        popped_color = len(rensa)
        print('popped_color : ', popped_color)
        tmp_score = total_popped * 10
        rensa_multiplier = min(999, 2**(rensa_count+1)) if rensa_count >1 else 0
        color_multiplier = [0, 3, 6, 12, 24][popped_color-1]
        connected_multiplier = sum(sum(([0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7][n] if n<11 else 10) for n in c)for c in rensa)
        multiplier = min(999, rensa_multiplier + color_multiplier + connected_multiplier) or 1
        score += tmp_score * multiplier
        #print('%drensa score += %d * (%d + %d + %d)'% (rensa_count, tmp_score, rensa_multiplier, color_multiplier, max_connected_multiplier))
    return score

def show_rensa_information(rensas):
    score = get_score(rensas)
    jama = score // 70
    return '%d連鎖 %d点 おじゃまぷよ%d個 ' % (len(rensas), score, jama) + jama_representation(jama)


print("I'm alive!")
if local: # local testing
    context = "#Bpuyo"
    while 1:
        irc_parameters = input().split()
        irc_parameters = [context]+irc_parameters # to simulate IRC environment
        command = irc_parameters[1]
        if command == 'score':
            if len(irc_parameters) < 3:
                say(context, 
                    '変数が足りないです。利用方法：　!score 数-数-数/数&数 (-は連鎖、/は同時連鎖、&は同色同時連鎖)')
                continue
            rensas = parse_puyo(irc_parameters[2])
            say(context, show_rensa_information(rensas))

    quit()


s = socket.socket()
s.connect((host, port))

send('NICK', nick)
send('USER', (user, '0', '*', ':'+realname))
send('JOIN', puyo_channel)

def greeting_message():
    hour = datetime.datetime.now().hour
    return ['こんにちは', 'こんばんは'][hour>16 or hour < 4]
say(master, greeting_message() + '、マスター')
say(puyo_channel, greeting_message() + '！ Qriaのボットです。')

while 1:
    sleep(0.1)
    try: #server and channel encoding is different. this hack works it around
        read_buffer = read_buffer+s.recv(1024).decode(jp_encoding)
    except Exception as e:
        print(e)
        read_buffer = read_buffer+s.recv(1024).decode(default_encoding)
    temp = str.split(read_buffer, "\n")
    read_buffer = temp.pop()

    for line in temp:
        line = line.rstrip() # remove tailing whitespaces
        irc_command, irc_parameters, prefix = parse(line)
        if prefix and prefix.startswith(':'):
            prefix = prefix[1:]
        log(prefix, irc_command, irc_parameters)
        if irc_command == "PING":
            pong(irc_parameters[0])
        if irc_command == "PRIVMSG" and len(irc_parameters) > 1:
            # PRIVMSG irc_parameters = channel_or_Qbot :messages messages ...
            sender = prefix.split('!')[0]
            channel = irc_parameters[0]
            context = channel if channel.startswith('#') else sender
            assert irc_parameters[1][0] == ':'
            irc_parameters[1] = irc_parameters[1][1:]
            print(sender + ' sent message : "' + ' '.join(irc_parameters[1:]) + '" in channel ' + channel + ' on context '+context)
            if irc_parameters[1].startswith(command_character) \
                    and len(irc_parameters[1]) > len(command_character): # ignores if just one '!'
                command = irc_parameters[1][len(command_character):]
                if sender == master: # master irc_commands
                    print('command', command)
                    if command == 'die':
                        say(context, 'かしこまりました')
                        send("QUIT", ':死亡')
                        quit()
                    elif command == 'command':
                        if len(irc_parameters < 3):
                            say(context, '変数が足りないです。利用方法：　!command (command) [params...]')
                            continue
                        send(irc_parameters[2], irc_parameters[3:])
                    elif command == 'restart':
                        say(context, '再起動します')
                        reload = True
                        say(context, '...でも再起動の方法がわからないです')
                    elif command == 'ping':
                        say(context, '生きてます。')

                # non-master commands
                if command == 'rank':
                    if len(irc_parameters) < 3:
                        name = sender
                    else:
                        name = irc_parameters[2]
                    say(context, name + ' さんのランク： '+get_rank(name))
                elif command == 'score':
                    if len(irc_parameters) < 3:
                        say(context,
                            '変数が足りないです。利用方法： !score 数-数-数/数&数 (-は連鎖、/は同時連鎖、&は同色同時連鎖)')
                        continue
                    rensas = parse_puyo(irc_parameters[2])
                    say(context, show_rensa_information(rensas))
