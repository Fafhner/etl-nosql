
def count(tb):
    c = len(tb)
    return c


def inner_join(left_tb, left_idx, right_tb, right_idx):
    return left_tb.merge(right_tb, how='inner', left_on=left_idx, right_on=right_idx)


def outer_join(left_tb, left_idx, right_tb, right_idx):
    return left_tb.merge(right_tb, how='outer', left_on=left_idx, right_on=right_idx)


def left_join(left_tb, left_idx, right_tb, right_idx):
    return left_tb.merge(right_tb, how='left', left_on=left_idx, right_on=right_idx)


def right_join(left_tb, left_idx, right_tb, right_idx):
    return left_tb.merge(right_tb, how='right', left_on=left_idx, right_on=right_idx)


def intersect(left_tb, right_tb):
    return left_tb.merge(right_tb, on=None)


def sel_filter_sign(sign):
    if sign == '>':
        return lambda tb, col, val: tb[col] > val
    elif sign == '>=':
        return lambda tb, col, val: tb[col] >= val
    elif sign == '<':
        return lambda tb, col, val: tb[col] < val
    elif sign == '<=':
        return lambda tb, col, val: tb[col] <= val
    elif sign == '=':
        return lambda tb, col, val: tb[col] == val


def sel_filter_between_sign(sign):
    if sign == '><':
        return lambda tb, col, val1, val2: tb[col] > val1 & tb[col] < val2
    elif sign == '><=':
        return lambda tb, col, val1, val2: tb[col] > val1 & tb[col] <= val2
    elif sign == '>=':
        return lambda tb, col, val1, val2: tb[col] >= val1 & tb[col] < val2
    elif sign == '>=<=':
        return lambda tb, col, val1, val2: tb[col] >= val1 & tb[col] <= val2


def filter(tb, col, sign, val):
    return tb[sel_filter_sign(sign)(tb, col, val)]


def filter_between(tb, col, sign, val1, val2):
    return tb[sel_filter_between_sign(sign)(tb, col, val1, val2)]


func_map = {
    "count": count,
    "inner_join": inner_join,
    "outer_join": outer_join,
    "left_join": left_join,
    "right_join": right_join,
    "intersect": intersect,
    "filter": filter,
    "filter_between": filter_between,
}
