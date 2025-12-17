def is_balanced(s):
    stack = []
    for c in s:
        if c== '(':
            stack.append(c)
        elif c ==')':
            if not stack:
                return False
            stack.pop()
    return len(stack)==0

try:
    while True:
        line = input().strip()
        if line == "":
            break
        print("YES" if is_balanced(line) else "NO")
except EOFError:
    pass
