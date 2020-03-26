# 微分

切线方程：局部线性化

可微：y=f(x)在x0的某领域内有定义，如果f(x)在x0处的改变量delta_y=f(x0+delta_x)-f(x0)可以表示为：delta_y = A*delta_x+o(delta_x)，其中A仅与x0有关，则A*delta_x称为y=f(x)在x0处的微分，记为dy。

可见，微分dy是delta_x的线性函数，也即是dy是该变量delta_y的线性主要部分。

函数y=f(x)在x0处可微，则其在x0处可导，且A=f'(x0)。反之亦然。可得：dy/dx = f'(x)

## 01 运算法则

```python
d(u+v) = du+dv
d(u*v) = vdu+udv
d(u/v) = (vdu-udv)/v**2
对y=f(g(x)): dy/dx=f'(u)g'(x)
```

## 02 Python

```python
x = sympy.Symbol('x')
f = x ** 2 + 2 * x + 1
print(sympy.diff(f, x))

y = sympy.Symbol('y')
f = x**2 + 2*x*y + y**3
print(sympy.diff(f, x))
print(sympy.diff(f, y))
```


