def clculator(a, b, op):
    if op == 'add':
        return a + b
    elif op == 'sub':
        return a - b
    elif op == 'mul':
        return a * b
    elif op == 'div':
        if b == 0:
           return '除数不能为0'
        return a / b
    else:
        return '错误，不支持操作'

result = clculator(3,5,'add')
print(result)
