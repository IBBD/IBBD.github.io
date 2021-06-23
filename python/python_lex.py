# -*- coding: utf-8 -*-
#
# 将表达式格式化成标准样式
# TODO 如果要校验表达式的语法，只要梳理清楚那种数据后只能跟那种数据就可以了
# Author: caiyingyao
# Email: cyy0523xc@gmail.com
# Created Time: 2021-06-23
"""
Example:
>>> exp = '(小鹏 >= 2) and "P7 价格"'
>>> fmt_expression(exp)
... '("小鹏" >= 2) and "P7 价格" >= 1'
"""
import re
import ply.lex as lex

DEBUG = True    # 正式部署时，需要关闭测试模式

# 常量
KEYWORD = 'KEYWORD'  # 关键词
LPAREN = 'LPAREN'    # 左括号
RPAREN = 'RPAREN'    # 右括号
LOGIT = 'LOGIT'      # 逻辑操作
NEAR = 'NEAR'        # 距离
# SLASH = 'SLASH'      # 斜杠
CMP = 'CMP'          # 比较操作

# List of token names.
tokens = (
    KEYWORD,  # 关键词
    LPAREN,   # 左括号
    RPAREN,   # 右括号
    LOGIT,    # 逻辑操作
    CMP,      # 比较操作
    NEAR,     # near操作
)

# 分组
t_LPAREN = r'\('      # 只允许使用小括号
t_RPAREN = r'\)'
# t_SLASH = r'\/'
t_CMP = r'(\>\=)|(\<\=)|(\=)|(\>)|(\<)'
t_ignore  = ' \t'    # 忽略空格及tab


def t_KEYWORD(t):
    # 双引号内的，或者不非空格组成的字符串（不含括号）
    r'("[^\"]+")|([^\s\(\)\>\<\=\/][^\s\(\)]*)'
    val_lower = t.value.lower()
    if val_lower in {'and', 'or', 'not'}:
        t.type = LOGIT
        return t
    if val_lower.startswith('near'):   # 格式如：near/5
        t.type = NEAR
        return t
    if t.value[0] == '"':
        t.value = t.value[1:-1]    # 关键词统一去掉双引号
    return t


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


def fmt_expression(expression: str) -> str:
    """格式表达式
    Args:
        expression: 简化的表达式
    Returns:
        标准表达式
    """
    if DEBUG:
        print('')
    # 格式化near
    expression = re.sub('near\s*/\s*([\-\+]?\d+)', 'near/\g<1>', expression)
    # print(expression)
    lexer.input(expression)
    out_toks = []
    while True:
        tok = lexer.token()
        if not tok: 
            break
        if DEBUG:
            print(tok)
        out_toks.append(fmt_tok(tok))
    out_data = []
    total = len(out_toks)
    for ind, tok in enumerate(out_toks):
        if tok[0] != KEYWORD:
            out_data.append(tok[1])
        else:    # 关键词需要特殊处理
            if ind > 0 and out_toks[ind-1] == (LOGIT, 'not'):
                # 前面一个如果是not
                out_data.append(f'"{tok[1]}"')
            elif ind > 0 and out_toks[ind-1][0] == CMP:
                # 前面一个如果是比较符
                out_data.append(tok[1])
            elif ind < total-1:       # 不是最后一个
                if out_toks[ind+1][0] not in (CMP, NEAR):   # 关键词后面如果没有跟比较or near操作
                    out_data.append(f'"{tok[1]}" >= 1')
                else:
                    out_data.append(f'"{tok[1]}"')
            else:
                out_data.append(f'"{tok[1]}" >= 1')

    exp = ' '.join(out_data)
    exp = exp.replace('( ', '(')
    exp = exp.replace(' )', ')')
    return exp


def fmt_tok(tok: lex.LexToken):
    return tok.type, tok.value


if __name__ == '__main__':
    exp = '小鹏 and P7'
    new_exp = fmt_expression(exp)
    assert new_exp == '"小鹏" >= 1 and "P7" >= 1'

    # 带双引号的测试
    exp = '小鹏  and "P7 价格"'
    new_exp = fmt_expression(exp)
    assert new_exp == '"小鹏" >= 1 and "P7 价格" >= 1'

    # 带括号及比较操作的测试
    exp = '(小鹏 >= 2) and "P7 价格"'
    new_exp = fmt_expression(exp)
    assert new_exp == '("小鹏" >= 2) and "P7 价格" >= 1'

    # near
    exp = '蔚来 near/3 汽车'
    new_exp = fmt_expression(exp)
    assert new_exp == '"蔚来" near/3 "汽车" >= 1'

    # near
    exp = '蔚来 near /3 汽车'
    new_exp = fmt_expression(exp)
    assert new_exp == '"蔚来" near/3 "汽车" >= 1'

    # 复杂语句
    exp = '(小鹏  and (p7 or g3) and 小鹏 near/5 p7 or 小鹏 near/5 g3)>=12 and not 威马 and  not 吉利'
    cmp_exp = '("小鹏" >= 1 and ("p7" >= 1 or "g3" >= 1) and "小鹏" near/5 "p7" >= 1 or "小鹏" near/5 "g3" >= 1) >= 12 and not "威马" and not "吉利"'
    new_exp = fmt_expression(exp)
    assert new_exp == cmp_exp
