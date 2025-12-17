def is_balanced(s):
    stack = []
    for c in s:
        if c == '(':
            stack.append(c)
        elif c == ')':
            if not stack:
                return 0
            stack.pop()
    return 1 if len(stack) == 0 else 0

s = input().strip()
print(is_balanced(s))