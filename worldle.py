import itertools

# print(list(itertools.permutations(["u","n","g","s"])))

for x in list(itertools.permutations(["y","i","e","d"])):
    if ("y" is x[0]):
        if ("i" is x[1]):
            if ("e" is not x[2] and "t" is not x[3]):
                if ("d" is not x[3] and "e" is not x[1]):
                    print(x)