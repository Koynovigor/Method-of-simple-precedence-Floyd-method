# coding=windows-1251
# # Метод простого предшествования (с использованием функций предшествования, построенных итерационным методом Флойда)
import re
import TableIt
import copy

TERMS = ["!", "+", "*", "(", ")", "a", "b"]
N_TERMS = ["A", "B", "B`", "T", "T`", "M"]
RULES = {
    "A": ["!B!"],
    "B": ["B`"],
    "B`": ["T", "B`+T"],
    "T": ["T`"],
    "T`": ["M", "T`*M"],
    "M": ["a", "b", "(B)"]
}

RULES_INDEX = {
    "!B!": '1',
    "B`": '2',
    "T": '3',
    "B`+T": '4',
    "T`": '5',
    "M": '6',
    "T`*M": '7',
    "a": '8',
    "b": '9',
    "(B)": '10'
}

# Построение множеств крайних правых и крайних левых символов
def build_L_R_set(L, R):
    for non_term in RULES:
        L[non_term] = []
        R[non_term] = []
    for non_term in L:
        for right_rule in RULES.get(non_term):
            # первый случай, когда в правой части стоит один символ
            if N_TERMS.count(right_rule) or TERMS.count(right_rule):
                L[non_term].append(right_rule)
                R[non_term].append(right_rule)
            # T`*M, B`+T
            if re.search("(`)[+*]", right_rule) is not None:
                if not L[non_term].count(right_rule[:len(right_rule) - 2]):
                    L[non_term].append(right_rule[:len(right_rule) - 2])
                if not R[non_term].count(right_rule[-1]):
                    R[non_term].append(right_rule[-1])
            # (B) (A) !T! !B!
            if re.search("(!|\()[A-Z]", right_rule) is not None:
                L[non_term].append(right_rule[:len(right_rule) - 2])
                R[non_term].append(right_rule[-1])
    for non_term in N_TERMS:
        for el in L[non_term]:
            if N_TERMS.count(el):
                for term in L[el]:
                    if not L[non_term].count(term):
                        L[non_term].append(term)
        for el in R[non_term]:
            if N_TERMS.count(el):
                for term in R[el]:
                    if not R[non_term].count(term):
                        R[non_term].append(term)

def build_matrix(L, R):
    s_i = [')', 'a', 'b', 'M', '*', 'T`', 'T', '+', 'B`', 'B', '(', '!']
    s_j = [' ', '(', 'a', 'b', 'M', '*', 'T`', 'T', '+', 'B`', ')', 'B', '!']
    matrix = [[' ' for c in range(len(s_i) + 1)] for r in range(len(s_i) + 1)]
    matrix[0] = s_j
    for r in range(len(matrix)):
        for c in range(len(matrix)):
            if c == 0 and r > 0:
                matrix[r][c] = s_i[r - 1]
    # формируем правила, которые длиной больше 1
    vector_rules = []
    for rule in RULES:
        for right_rule in RULES.get(rule):
            if len(right_rule) > 1 and right_rule not in N_TERMS:
                vector_rules.append(right_rule)
    for rule in range(len(vector_rules)):
        vector_rules[rule] = list(vector_rules[rule])
        if '`' in vector_rules[rule]:
            idx = vector_rules[rule].index('`')
            vector_rules[rule][idx - 1] += vector_rules[rule][idx]
            vector_rules[rule].remove('`')
    # определяем отношение равенства =.
    for rule in vector_rules:
        for idx_el in range(len(rule) - 1):
            # print(f'{rule[idx_el]}{rule[idx_el + 1]}')
            idx_s_j = 0
            idx_s_i = 0
            for r in range(len(s_i)):
                if rule[idx_el] == s_i[r]:
                    idx_s_i = r + 1
            for r in range(len(s_j)):
                if rule[idx_el + 1] == s_j[r]:
                    idx_s_j = r
            matrix[idx_s_i][idx_s_j] = '=.'
    # определяем отношение равенства <.
    # T <. N
    for rule in vector_rules:
        for idx_el in range(len(rule) - 1):
            if rule[idx_el] in TERMS and rule[idx_el + 1] in N_TERMS:
                # print(f'{rule[idx_el]}{rule[idx_el + 1]}')
                idx_s_i = 0
                for r in range(len(s_i)):
                    if rule[idx_el] == s_i[r]:
                        idx_s_i = r + 1
                for term_from_L in L.get(rule[idx_el + 1]):
                    for k in range(len(s_j)):
                        if term_from_L == s_j[k]:
                            matrix[idx_s_i][k] = '<.'
    # определяем отношение равенства .>
    # N .> T
    for rule in vector_rules:
        for idx_el in range(len(rule) - 1):
            if rule[idx_el] in N_TERMS and rule[idx_el + 1] in TERMS:
                # print(f'{rule[idx_el]}{rule[idx_el + 1]}')
                idx_s_j = 0
                for r in range(len(s_j)):
                    if rule[idx_el + 1] == s_j[r]:
                        idx_s_j = r
                # print(R.get(rule[idx_el]))
                for term_from_R in R.get(rule[idx_el]):
                    for k in range(len(s_i)):
                        if term_from_R == s_i[k]:
                            matrix[k + 1][idx_s_j] = '.>'

    return matrix

def build_functions(matrix):
    f = {}
    g = {}
    for i in range(1, len(matrix)):
        f[matrix[0][i]] = 1
        g[matrix[0][i]] = 1
    f_copy = {}
    g_copy = {}
    while f_copy != f or g_copy != g:
        f_copy = copy.deepcopy(f)
        g_copy = copy.deepcopy(g)
        for j in range(len(matrix)):
            for i in range(len(matrix)):
                if matrix[i][j] == '.>' and f.get(matrix[i][0]) <= g.get(matrix[0][j]):
                    f[matrix[i][0]] = g[matrix[0][j]] + 1
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if matrix[i][j] == '<.' and f.get(matrix[i][0]) >= g.get(matrix[0][j]):
                    g[matrix[0][j]] = 1 + f[matrix[i][0]]
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if matrix[i][j] == '=.' and f.get(matrix[i][0]) != g.get(matrix[0][j]):
                    maximum = max(g[matrix[0][j]], f[matrix[i][0]])
                    g[matrix[0][j]] = maximum
                    f[matrix[i][0]] = maximum
    return f, g

def translator(f, g, string):
    res = ""
    # переносим первый символ в стек и удаляем его из строки
    stack = [string[0]]
    string = string[1:]
    while stack[0] != "A":
        # если цепочка вся прочитана
        if len(string) == 0:
            reduce = []
            reduce = [stack.pop()] + reduce
            while len(stack) > 0 and f[stack[len(stack) - 1]] >= g[reduce[0]]:
                reduce = [stack.pop()] + reduce
            rule = "".join(x for x in reduce)
            flag = True
            for non_term in RULES.keys():
                for r in RULES.get(non_term):
                    if r == rule:
                        res = res + RULES_INDEX.get(r) + " "
                        flag = False
                        stack.append(non_term)
                        break
            if flag:
                res = "Строка не принадлежит грамматике"
                break
            continue
        # если между вершиной стека и текущим символом входной цепочки нет отношения .>
        if f[stack[len(stack) - 1]] <= g[string[0]]:
            stack.append(string[0])
            string = string[1:]
            continue
        # если между вершиной стека и текущим символом входной цепочки есть отношение .>
        if f[stack[len(stack) - 1]] > g[string[0]]:
            reduce = []
            reduce = [stack.pop()] + reduce
            while len(stack) > 0 and f[stack[len(stack) - 1]] >= g[reduce[0]]:
                reduce = [stack.pop()] + reduce

            rule = "".join(x for x in reduce)

            flag = True
            for non_term in RULES.keys():
                for r in RULES.get(non_term):
                    if r == rule:
                        res = res + RULES_INDEX.get(r) + " "
                        flag = False
                        stack.append(non_term)
                        break
            if flag:
                res = "Строка не принадлежит грамматике"
                break
            continue

        res = "Строка не принадлежит грамматике"
        break
    print(res)
    return res


def main():
    L = {}
    R = {}
    build_L_R_set(L, R)
    matrix = build_matrix(L, R)
    f, g = build_functions(matrix)
    string = "!(a+b)*(a*b)!"
    translator(f, g, string)
    #TableIt.printTable(matrix, useFieldNames = True)

if __name__ == "__main__":
    main()
