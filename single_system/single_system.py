import random
import string
# Create random links

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    # print("Random string of length", length, "is:", result_str)
    end_dot = ['gr', 'com', 'org', 'edu', 'eu']
    return 'http://'+result_str+'.' + end_dot[random.randint(0, len(end_dot)-1)]

my_list = []
for i in range(1000):
    my_list.append(get_random_string(random.randint(1,20)))

with open("fout.txt", "w") as fout:
    print(*my_list, sep="\n", file=fout)