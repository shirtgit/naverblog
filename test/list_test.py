from data import list_data

a = []
b = [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6]]

def func(c):
    global a
    a = c

func([(row[0], row[1]) for row in b])
print(a)
