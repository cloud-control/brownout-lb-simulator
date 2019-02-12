import os

targ = "result"
subf = "sim"
incr = 5

# Find directories
dirs = [x[0] for x in os.walk(targ)]
new_dirs = {}

for path in dirs:
    s = path.split(subf)
    if len(s) == 2:
        s_new = s[0] + subf + str(int(s[1])+incr)
        os.rename(path, s_new)

    elif len(s) > 2:
        raise ValueError("Paths contains more than one of the substring!")

