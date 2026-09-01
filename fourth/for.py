def f():
    for i in range (10):
        yield i

y = f()
print(y)