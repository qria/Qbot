# Todo : next puyo generation
# Todo : resolve puyo board popping spree
# Todo : set win condition
# Todo : calculate time accurately
# Todo : calcualte popping resolve time


from color import white, red, green, blue, yellow, purple
from collections import defaultdict
from random import randint
#temp: merge the variables plz
local = False # for local debugging


# game constants
board_height = 7
board_width = 6
color_count = 4
jama_rate = 70
RED, GREEN, BLUE, YELLOW, PURPLE = (1, 2, 3, 4, 5)
PUYO_TYPE = [RED, GREEN, BLUE, YELLOW, PURPLE]
def jama(s):
    return '◎'
puyo_shapes = [color(('●')) for color in [white, red, green, blue, yellow, purple, jama]]
if local:
    puyo_shapes = ['　', '①', '②', '③', '④', '⑤', '◎', '■']


# game variables init

game_started = False
boards = dict()
player_turn_count = dict()
next_puyo = dict()
player_time = dict()


# game functions

def print_boards(boards, messages = None):
    if not messages:
        messages = []
    board1, board2 = boards[1], boards[2]
    assert len(board1) == len(board2)

    results = [""] * len(board1)
    separation = 10

    for i, puyo_row in enumerate(reversed(board1)):
        results[i] += "■" + ''.join(puyo_shapes[puyo] for puyo in puyo_row) + "■"
    for i in range(len(board1)):
        results[i] += ' ' * separation
    for i, puyo_row in enumerate(reversed(board2)):
        results[i] += "■" + ''.join(puyo_shapes[puyo] for puyo in puyo_row) + "■"
    results.append("■" * 8 + " " * separation + "■" * 8)

    if len(messages) > len(results):
        print('Message length longer than board length!!!')
    for i in range(len(messages)):
        results[len(board1)-len(messages)+i+1] += ' ' * separation + messages[i]
    return results



"""
game board : flipped upside down,
    0 is blank, 1 to 5 is red green blue yellow purple. 6 is jama, 7 is solid block.
ex :
[   [1, 1, 1, 2, 2, 0],
    [2, 3, 1, 0, 0, 0],
    [3, 3, 2, 0, 0, 0],
    [0, 3, 2, 0, 0, 0], ...
 ] # 2rensa double

"""



def generate_random_puyo(): # generates random puyo set when called
    return randint(1, color_count), randint(1, color_count)


def init_game():
    global boards, player_turn_count, next_puyo, player_time, game_started

    boards[1], boards[2] = [[0]*board_width for i in range(board_height)], [[0]*board_width for i in range(board_height)]
    player_turn_count[1], player_turn_count[2] = 1, 1
    next_puyo = defaultdict(generate_random_puyo)
    player_time[1], player_time[2] = 0, 0
    game_started = True

def flood(board, coordinate, flooder, original_color = None):
    i, j = coordinate
    if original_color is None:
        original_color = board[j][i]
    #print('flood :', 'i :', i, ' j:', j, ' original_color : ', original_color)

    popped_count = 0
    board[j][i] = flooder
    popped_count += 1

    if i > 0 and board[j][i-1] == original_color:
        popped_count += flood(board, (i-1, j), flooder, original_color)
    if i < board_width - 1  and board[j][i+1] == original_color:
        popped_count += flood(board, (i+1, j), flooder, original_color)
    if j > 0 and board[j-1][i] == original_color:
        popped_count += flood(board, (i, j-1), flooder, original_color)
    if j < board_height - 1 and board[j+1][i] == original_color:
        popped_count += flood(board, (i, j+1), flooder, original_color)

    return popped_count

def resolve_board(board):
    """
    :param board: puyo board
    :return: elapsed time
    """
    # pop, drop, loop
    elapsed_time = 0
    rensa = 1
    flooded = -999 # constant to indicate flooded value
    blank = 0  # constant to indicate empty space
    while 1:
        something_changed = False
        score = 0
        total_popped = 0
        popped_color = set()
        max_connected_count = 0


        # pop via floodfill
        for j, puyo_row in enumerate(board):
            for i, puyo in enumerate(puyo_row):
                #print('checking ', (i,j))
                if puyo not in PUYO_TYPE:
                    continue
                tmp = puyo
                popped_count = flood(board, (i, j), flooded)
                if popped_count < 4:
                    #print('rewinding')
                    flood(board, (i, j), tmp)
                    continue
                flood(board, (i, j), blank)
                total_popped += popped_count
                popped_color.add(tmp)
                max_connected_count = max(max_connected_count, popped_count)
                something_changed = True


        # dropping
        for i in range(board_width):
            puyo_column = [board[j][i] for j in range(board_height)]
            while puyo_column and puyo_column[0] == 0:
                puyo_column.pop(0)
            for j in range(board_height):
                board[j][i] = puyo_column[j] if j < len(puyo_column) else 0

        if not something_changed:
            break

        score = total_popped * 10
        rensa_multiplier = min(999, 2**(rensa+1)) if rensa >1 else 0
        color_multiplier = [0, 3, 6, 12, 24][len(popped_color)-1]
        max_connected_multiplier = [0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7][max_connected_count] if max_connected_count<11 else 10

        print('%s rensa, score : %s * (%s+%s+%s)'
              % (rensa, score, rensa_multiplier, color_multiplier, max_connected_multiplier))
        multiplier = rensa_multiplier + color_multiplier + max_connected_multiplier
        score *= multiplier
        elapsed_time += 1
        rensa += 1

    return elapsed_time


def current_player():
    return [1, 2][player_time[1] > player_time[2]]


def show_game_state(context=None):
    # Todo : clean these mess
    current_next_puyos = [ [ next_puyo[player_turn_count[1]][0], next_puyo[player_turn_count[1]][1] ],
                           [ next_puyo[player_turn_count[2]][0], next_puyo[player_turn_count[2]][1] ] ]
    messages = ['NEXT',
                puyo_shapes[current_next_puyos[0][0]] + ' '*5 + puyo_shapes[current_next_puyos[1][0]],
                puyo_shapes[current_next_puyos[0][1]] + ' '*5 + puyo_shapes[current_next_puyos[1][1]],
                'プレイヤ1：ターン'+str(player_turn_count[1])+'目, 約 ' + str(player_time[1]) + '秒',
                'プレイヤ2：ターン'+str(player_turn_count[2])+'目, 約 ' + str(player_time[2]) + '秒',
                'プレイヤ'+str(current_player()) + 'のターンです']
    say(context, print_boards(boards, messages))


def put_puyo(direction, n):
    if direction.lower() not in 'usmh':
        return False
    try:
        n = int(n)
    except Exception as e:
        return False
    if n < 1 or n > board_width:
        return False
    if n == 1 and direction == 'h' or n == board_width and direction == 'm':
        return False

    global boards, player_turn_count, next_puyo, player_time
    player = current_player()
    turn = player_turn_count[player]
    board = boards[player]

    if direction == 's':
        for i in range(len(board)-1):
            if not board[i][n-1]: # empty spot found
                board[i][n-1] = next_puyo[turn][0]
                board[i+1][n-1] = next_puyo[turn][1]
                break
        else:
            return False # todo : death
    elif direction == 'u':
        for i in range(len(board)-1):
            if not board[i][n-1]: # empty spot found
                board[i][n-1] = next_puyo[turn][1]
                board[i+1][n-1] = next_puyo[turn][0]
                break
        else:
            return False
    elif direction == 'm':
        for i in range(len(board)):
            if not board[i][n-1]:
                board[i][n-1] = next_puyo[turn][1]
                break
        for i in range(len(board)):
            if not board[i][n]:
                board[i][n] = next_puyo[turn][0]
                break
    elif direction == 'h':
        for i in range(len(board)):
            if not board[i][n-1]:
                board[i][n-1] = next_puyo[turn][1]
                break
        for i in range(len(board)):
            if not board[i][n-2]:
                board[i][n-2] = next_puyo[turn][0]
                break

    player_turn_count[player] += 1
    player_time[player] += 1
    player_time[player] += resolve_board(board)
    #todo: jama
    return True