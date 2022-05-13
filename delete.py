
import itertools

# print(list(itertools.permutations(["u","n","g","s"])))

for x in list(itertools.permutations(["u","n","g","s"])):
    if ("u" is not x[0]):
        if ("n" is not x[1]):
            if ("g" is not x[2]):
                if ("s" is not x[3]):
                    print(x)