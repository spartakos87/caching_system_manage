from random import randint
import csv
# Read links
links = []
with open('fout.txt') as f:
    for line in f:
        links.append(line.split('\n')[0])
cache = []
hit = 0
miss = 0
data = []
for i in range(10000):
    url = links[randint(0, len(links)-1)]
    if url in cache:
        hit += 1
        print("HIT:{} , MISS:{}, REQUEST:{}".format(hit, miss, i))
    else:
        print("MISS")
        miss += 1
        cache.append(url)
        print("HIT:{} , MISS:{}, REQUEST:{}".format(hit, miss, i))
    data.append([hit, miss, i])

# with open("data.txt", "w") as f:
#     print(*data, sep="\n", file=f)
with open('output.csv','w') as f:
    writer = csv.writer(f)
    writer.writerows(data)