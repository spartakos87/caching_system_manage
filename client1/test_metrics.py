import os
from time import sleep
from subprocess import check_output
from random import randint, random
import csv

# Read links
links = []
with open('fout.txt') as f:
    for line in f:
        links.append(line.split('\n')[0])

hit = 0
miss = 0
data = []
for i in range(10000):
    # sleep(random(0.5, 1.5))
    url = links[randint(0, len(links)-1)]
    try:
        res = check_output('python3 custom_get_request.py '+url, shell=True)
        if '0' in str(res):
            miss += 1
        else:
            hit += 1
        print("CLIENT 1==> HIT:{}, MISS:{}, REQUESTS:{}".format(hit, miss, i))
        data.append([hit, miss, i])
    except:
        print("PASS")
        pass
    # os.system('python3 custom_get_request.py ' + url)

with open('output_client_1.csv','w') as f:
    writer = csv.writer(f)
    writer.writerows(data)