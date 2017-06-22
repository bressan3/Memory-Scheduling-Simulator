from random import randint

num_list = []

for i in xrange(0, 3500):
    current = randint(0, 127)
    if i > 0:
        while current == num_list[i-1]:
            current = randint(0, 7)
    num_list.append(current)


# print num_list[0:4]
# print num_list[0:8]
# print num_list[0:16]
# print num_list[0:32]
# print num_list[0:64]
# print num_list[0:128]
# print num_list[0:256]
# print num_list[0:512]
print num_list[0:5120]
