import sys, os
import const


path = os.path.join(STAMP_PATH, "text", "font.txt")
if not os.exists(path):
    print path + " not found"
lines_in = open('font.txt', 'r').readlines()
num_chars = len(lines_in)/7

chars = dict()
print str(num_chars) + " characters in font.txt"
for i in range(num_chars):
    tlines = lines_in[7*i : 7*i + 7]

    # get character  
    tchar = tlines[0][:-1] # remove NL

    # get width of character
    width = int(tlines[1].strip())
    # print (str(width) + ": \"" + str(tchar) + "\"")

    # remove newline and comine rows into one string
    char_string = ""
    for j in xrange(5): # j = row#
        tmp = tlines[j+2][:-1] + "     "
        tlines[j+2] = tmp[:width]
        char_string += tlines[j+2]
        # print tlines[j+2]
    # print char_string
  
  
    chars[tchar] = [(width, 5), char_string]
print sorted(chars.keys())