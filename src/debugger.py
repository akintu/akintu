import pdb
import akintu
import datetime
import os
from const import *
import cProfile, pstats, io

now = datetime.datetime.now()
path = os.path.join(SAVES_PATH, "profile")
if not os.path.exists(path):
    os.makedirs(path)

filename = os.path.join(path, str("cprofile_" + str(now.strftime("%d_%H%M")) + ".txt"))
# cProfile.run("akintu.main()", filename)

#!!!IF YOU DON'T WANT TO JOIN EVERY PROFILE IN THE DIRECTORY, INVERT THIS SECTION!!!
# p = pstats.Stats(filename) 
list = os.listdir(path)
p = pstats.Stats(os.path.join(path, list[0]))
for file in list[1:]:
    file = os.path.join(path, file)
    if file != filename:
        p.add(file)
##################     END SECTION     ########################

p.strip_dirs().sort_stats(-1)
p.sort_stats('time').print_stats(25)
p.sort_stats('cumulative').print_stats(25)
