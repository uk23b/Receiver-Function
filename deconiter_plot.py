import obspy,os
import matplotlib.pyplot as plt
import numpy as np
from obspy.geodetics import kilometers2degrees
from obspy.taup import TauPyModel
from obspy.taup import TauPyModel
from decon import deconit as deconiti


source_path = r'/Volumes/UNTITLE/09_decon_iter/done/'

station = 'QUB'
station_rf = os.path.join(source_path,station)
#print(station_rf)
files = os.listdir(station_rf)
#print(files)
for f in files:
    filename = station + '_rf.png'
    files_m = os.path.join(station_rf,f)
    #print(files_m)
    if '.sac' in f:
        print(f)
        #event_file = os.path.join(files_m,f)
        st = obspy.read(files_m)
        tr = st[0]
        #fig = plt.figure()
        #ax = fig.add_subplot(1, 1, 1)
        plt.plot(tr.times("relative")-5, tr.data, "b-", linewidth=0.05,)
        plt.ylim(-2, 2)
        plt.savefig(filename)









