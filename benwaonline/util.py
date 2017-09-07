import random
from os import listdir
from os.path import isfile, join

def random_benwa(benwa_folder):
    _files = [f for f in listdir(benwa_folder) if isfile(join(benwa_folder, f))]
    benwa = random.choice(_files)
    return benwa

def benwa_username():
    numb = ['420', '69']
    joiner = ['xXx', '_', '']
    adj = ['lover', 'liker', 'hater']
    username = random.choice(adj).join(['benwa', random.choice(numb), random.choice(adj)])

    return username
