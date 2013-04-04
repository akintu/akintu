import sys

lines_in = open('font.txt', 'r').read()
output = lines_in.replace("#","+")
fout = open('font2.txt', 'w')
fout.write(output)
fout.close()
lines_in.close()
