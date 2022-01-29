import re
import sys


BUILD_PATTERN = re.compile(r'^(#define\s+VERSION_BUILD\s+)(\d+)(.*)$')

if __name__ == '__main__':
    fn = 'version.h'
    with open(fn, encoding='utf-8') as f:
        lines = f.read().splitlines()

    for i, line in enumerate(lines):
        m = BUILD_PATTERN.match(line)
        if m:
            g = m.groups()
            build = int(g[1]) + 1
            lines[i] = '%s%s%s' % (g[0], build, g[2])

    with open(fn, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write('%s\n' % line)

