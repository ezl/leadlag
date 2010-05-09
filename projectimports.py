import h5py
import numpy as np
from matplotlib import pyplot

from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed("Dropping to IPython shell")

filename = "SPY-VXX-20090507-20100427.hdf5"

start_day = 1
end_day = 245

#start_day = 108
#end_day = 111

start_day = 120
end_day = 245
start_day = 1
end_day = 120
start_day = 120
end_day = 180
start_day = 0
end_day = 245

days = end_day - start_day
