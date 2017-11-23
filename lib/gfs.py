def monotonically_increasing(l):
    return all(x < y for x, y in zip(l, l[1:]))
