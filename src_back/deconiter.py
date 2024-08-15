import obspy,os
from obspy.signal.trigger import recursive_sta_lta, trigger_onset
import matplotlib.pyplot as plt
from obspy.geodetics import kilometers2degrees
from obspy.taup import TauPyModel
import numpy as np
import seispy
from obspy.taup import TauPyModel
from decon import deconit as deconiti
import gc

#####  parameters ######

# window length for P wave detection by using STA_LTA. 
# Reference time is based on TauP traveltime curve
sta_lta_window = 10



window_length = 30 #seconds
max_filt = 1  #minimum end of bandpass filter (Hz)
min_filt = 0.2 #maximum end of bandpass filter (Hz)


m = open('sta_lta_out.txt', 'w')


target_path = r'/Volumes/UNTITLED/09_decon_iter/'


year = '2'
source_path = r'/Volumes/UNTITLED/03_extract_event/RF_events/'
#source_path = r'/Volumes/UNTITLED/06_STA_LTA/temp/'
year_events = os.path.join(source_path,year)

emp_event_name = set()
emp_staname = set()

wave_stream=obspy.Stream()
wave_trace= obspy.Trace()

wave_trace_rf= obspy.Trace()

#files = os.listdir(year_events)
event_folders = [ name for name in os.listdir(year_events) if os.path.isdir(os.path.join(year_events, name)) ]
for f in event_folders:
    files = os.path.join(year_events,f)
    print(files)
    file_paths = os.listdir(files)
    for i in file_paths:
        #print(i)
        if '.sac' in i:
            print(i)
            event_file = os.path.join(files,i)
            s1 = i.split(".")
            print(s1)
            s2 = s1[0].split("_")
            print(s2[1])
            emp_event_name.add(f)
            emp_staname.add(s2[1])

emp_event_name = list(emp_event_name)
emp_staname = list(emp_staname)

print(emp_staname)
print(emp_event_name)

for f in event_folders:
    files = os.path.join(year_events,f)
    #print(files)
    file_paths = os.listdir(files)
    for j in emp_staname:
        print(j)
        wave_stream.clear()
        for i in file_paths:
            if j in i:
                #print(i)
                event_file = os.path.join(files,i)
                st = obspy.read(event_file)
                print(st.get_gaps())
                print(st.print_gaps())
                
                if len(st) == 0:
                    continue
                
                st._trim_common_channels()
                st.trim(max(tr.stats.starttime for tr in st), min(tr.stats.endtime for tr in st))
                wave_stream += st

        wave_stream.sort(keys=['channel'], reverse = True)
        print(wave_stream)
        print('length of wave stream is ', len(wave_stream))


        for tr in st:
            station_name = tr.stats.station
            print(station_name)

            distance = tr.stats.sac.dist
            print('distance is :', distance, ' km')
            comp = tr.stats.channel
            direc = comp[2]
            df = tr.stats.sampling_rate
            cft = recursive_sta_lta(tr, int(2.5 * df), int(10. * df))
            #print('cft type is ', type(cft))
            on_of = trigger_onset(cft, 3.5, 0.5)
            maximum = np.max(cft)
            #print('cft is', (cft))
            max_ind = np.where(cft == maximum)
            #print((max_ind))
            maxval = max_ind[0]
            time = maxval / df
            time = time.astype(float)
            time = time[0]
            
            distance = tr.stats.sac.dist
            depth_meters = tr.stats.sac.evdp
            #print(depth_meters)
            depth_km = depth_meters
            #print('dist is ', distance, ' km')
            deg = kilometers2degrees(distance)

            
            depth_meters = tr.stats.sac.evdp
            #print(depth_meters)
            depth_km = depth_meters
            print('dist is ', depth_km, ' km')
            deg = kilometers2degrees(distance)

        if deg >= 20:
            
            if len(wave_stream) != 3:
                continue
            
            
            
            wave_trace_rf = wave_stream[0]

            wave_stream.detrend()
            wave_stream.filter("bandpass", freqmin=0.05, freqmax=2.0, zerophase=True)
            wave_stream.plot(show=False)

            da = seispy.distaz(wave_stream[0].stats.sac.stla, wave_stream[0].stats.sac.stlo, wave_stream[0].stats.sac.evla, wave_stream[0].stats.sac.evlo)
            dis = da.delta
            bazi = da.baz
            ev_dep = wave_stream[0].stats.sac.evdp
            print('Distance = %5.2f˚' % dis)
            print('back-azimuth = %5.2f˚' % bazi)

            comp_starttime = []
                
            #trim the data to have the same time span for rotation from NE to RT
            wave_stream.trim(max(tr.stats.starttime for tr in wave_stream), min(tr.stats.endtime for tr in wave_stream))

            st_TRZ = wave_stream.copy().rotate('NE->RT', back_azimuth=bazi)
            st_TRZ.plot(show=False)

            model = TauPyModel(model='iasp91')
            #arrivals = model.get_travel_times(ev_dep, dis, phase_list=['P'])
            
            arrivals = model.get_travel_times(source_depth_in_km=depth_km,distance_in_degree=deg, phase_list=["P"])
            #print(arrivals)
            #print(type(arrivals))
            
            if not arrivals:
                continue
                
            arr = arrivals[0]

            #print(type(arr))
                
            ray_parameter = arr.ray_param
            p_arrive_times = arr.time
            ray_incidence = arr.incident_angle
            print('ray parameter is ', ray_parameter)
            print('p wave arrive time is ', p_arrive_times)
            print('incidence angle is ', ray_incidence)
            
            window_minimum = p_arrive_times - window_length
            window_maximum = p_arrive_times + window_length
            
            rounded_start = round(window_minimum)
            rounded_end = round(window_maximum)
            
            print('starting time of P wave window is ',rounded_start)
            print('ending time of P wave window is ', rounded_end)
            
            rounded_start_ind = int(rounded_start * df)
            rounded_end_ind  = int(rounded_end * df)
            
            possible_p_window_trig = cft[rounded_start_ind:rounded_end_ind]
            possible_p_window_trace = tr[rounded_start_ind:rounded_end_ind]
            print(possible_p_window_trig)
            
            print('starting index of P wave window is ', rounded_start_ind)
            print('ending index of P wave window is ', rounded_end_ind )
            
            maximum_p_wind = np.max(possible_p_window_trig)


            #maximum_p_wind = np.argpartition(possible_p_window_trig, -3)[-3:]
            print('maximum_p_wind is ', maximum_p_wind)
            max_ind_P_wind = np.where(possible_p_window_trig == maximum_p_wind)
            print('max_ind_P_wind is ', max_ind_P_wind)
            print('maximum ind of P wind is ',max_ind_P_wind)
            maxval_P_wind = rounded_start_ind + ( max_ind_P_wind[0])
            print(maxval_P_wind)

            time_detect =  maxval_P_wind / df
            #time_detect =  maxval_P_wind
            print('time detect is', time_detect)
            time_detect = time_detect.astype(float)
            time_detect = time_detect[0]

            print('time detect is:', time_detect)
            print('seispy detect is:', arr)

            tr.stats.sac.user7=float(time_detect)
            tr.stats.sac.t7=float(time_detect)

            tr.stats.sac.user9 = float(maximum_p_wind)
            tr.stats.sac.t9 = float(maximum_p_wind)

            m.write("%s %5.5f %5.7f %5.7f %5.7f %5.4f\n" % (event_file, float(maximum_p_wind), float(tr.stats.sac.user8), ray_parameter, ray_incidence, float(tr.stats.sac.gcarc)))


            P_arr = arrivals[0]
            print(P_arr)

            arr = time_detect
            

            shift = 5
            time_after = 60

            st_TRZI=st_TRZ.decimate(1, strict_length=False, no_filter=True)
            st_TRZI=st_TRZI.trim(st_TRZI[0].stats.starttime+P_arr.time-shift,st_TRZI[0].stats.starttime+P_arr.time+time_after)
            #st_TRZI.plot(show=True)
            print(len(st_TRZI[0].data))

            rf = deconiti(uin=st_TRZI[1], win=st_TRZI[0], dt=st[0].stats.delta, nt=None, tshift=5, f0=2, itmax=400, minderr=0.001, phase='P')


            print(type(rf[0]))
            #print(list(rf[0]))
            print(len(rf[0]))
            wave_trace_rf.data = rf[0]

            print(len(rf[0]))
            time_axis = st_TRZI[0].times() - shift
            print(len(time_axis))

            file_rf_name = f+'_'+station_name + '_rf.png'
            filename_sac = f+'_'+station_name + '_rf.sac'
            print(file_rf_name)

            plt.plot(time_axis,rf[0])

            sta_out_folder = os.path.join(target_path,'done')
            sta_out_folder_stations = os.path.join(sta_out_folder,j)
            if not os.path.exists(sta_out_folder_stations):
                os.makedirs(sta_out_folder_stations)

            out_rf_filepath = os.path.join(sta_out_folder_stations,file_rf_name)
            out_rf_filepath_sac = os.path.join(sta_out_folder_stations,filename_sac)


            wave_trace_rf.write(out_rf_filepath_sac,format='SAC')

            plt.xlim(-shift, time_after + shift)
            plt.ylim(-1, 1)
            plt.savefig(out_rf_filepath)

            wave_stream.clear()
            st_TRZ.clear()
            st_TRZI.clear()
            st.clear()
            plt.clf()
            plt.cla()

            # clear memory
    # del wave_trace_rf
    # del wave_stream
    # del st_TRZ
    # del st_TRZI
    # del st
        gc.collect()
        plt.close('all')


m.close()
print('done')
