import re

castles_emoji = ["🌹", "🖤","☘️","🐢","🦇","🍁","🍆"]
def find_word(message):
    res = []
    r = [re.findall(i,message) for i in castles_emoji]
    for i in r:
        if i != []:
            res.append(i[0])
        else:
            pass
    return res
