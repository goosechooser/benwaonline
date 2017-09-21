from random import choice

def random_username(num=['420', '69'], connect=['xXx', '_', ''], adj=['lover', 'liker', 'hater']):
    username = choice(connect).join(['benwa', choice(adj), choice(num)])
    return {'name' : username}
