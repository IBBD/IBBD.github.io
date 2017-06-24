

# 1. 链式比较操作
print('*'*40)
print('链式比较')
age = 20
if 18 < age < 22:
    print(True)

# 2. if/else三目运算
print('*'*40)
print('if/else三目运算')
age = 'young' if age < 25 else 'not young'

# 3. 真值判断
print('*'*40)
print('真值判断')
attr = True
values = []
if attr == True:
    print(True)

if len(values) != 0:
    print('not eq 0')

## pythonic的写法应该如下
if attr:
    print(True)

if values:
    print('not eq 0')

# 4. for/else语句
print('*'*40)
print('for/else语句')
a_list = range(4)
for i in a_list:
    if i == 6:
        break

else:
    print('6 not in list')

for i in a_list:
    if i == 3:
        break

else:
    print('3 in list')

# 5. 字符串格式化
print('*'*40)
print('字符串格式化')
s = "hello {name}!".format(name='world')
print(s)

# 6. 列表切片
print('*'*40)
print('列表切片')
items = range(10)
print(items[1:4])
print(items[1::2])
print(items[:])

# 7. 善用生成器
print('*'*40)
print('善用生成器')
def fib(n):
    a, b = 0, 1
    while a < n:
        yield a
        a, b = b, a+b

print("fib(10):", list(fib(10)))

# 8. 获取字典元素
print('*'*40)
print('获取字典元素')
d = {'hello': 'world'}
print(d.get('hello', 'default value'))

# 9. 设置字典默认值
print('*'*40)
print('设置字典默认值')
a_dict = {}
data = [('a', 10), ('b', 20), ('a', 5)]
for (key, val) in data:
    a_dict.setdefault(key, []).append(val)

print(a_dict)

# 10. 字典推导式
print('*'*40)
print('字典推导式')
a_list = range(5)
a_dict = {v: v*2 for v in a_list if v % 2}
print(a_dict)

# 11. 字符串反转
print('*'*40)
print('字符串反转')
s = "hello world!"
print(s[::-1])

# 12. 使用zip创建键值对
print('*'*40)
print('使用zip创建键值对')
keys = ['Name', 'Sex', 'Age']
values = ['Tim', 'Male', 23]
print(dict(zip(keys, values)))

# 13. with文件操作
filename1 = "./pythonic.md"
with open(filename1) as r:
    lines = r.readlines()

filename2 = './hello.txt'
with open(filename2, "w") as w:
    pass

with open(filename1) as r, open(filename2, 'w') as w:
    pass
