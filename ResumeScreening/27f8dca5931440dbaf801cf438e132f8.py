def is_balanced(s):
    stack = []
    for c in s:
        if c == '(':
            stack.append(c)
        elif c == ')':
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0

s = input().strip()
print ("YES" if is_balanced(s) else "NO")