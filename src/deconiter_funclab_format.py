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
import subprocess

#files
# cut script
cut_name = 'DOCUT1'

# decon script
decon_name = 'DODECON'


#####  parameters ######
# window length for P wave detection by using STA_LTA. 
# Reference time is based on TauP traveltime curve
sta_lta_window = 10
window_length = 30 #seconds
max_filt = 1  #minimum end of bandpass filter (Hz)
min_filt = 0.2 #maximum end of bandpass filter (Hz)
gauss = 1.0 #gaussian filter width (Hz)

m = open('sta_lta_out.txt', 'w')

target_path = r'/Volumes/UNTITLE/final_gauss_1.0/'
# create the target folder if it does not exist
if not os.path.exists(target_path):
    os.makedirs(target_path)

source_path = r'/Volumes/UNTITLE/decimated_dn_1.0/'
# list only the folders in the source path
event_folders = [ name for name in os.listdir(source_path) if os.path.isdir(os.path.join(source_path, name)) ]
print(event_folders)

emp_event_name = set()
emp_staname = set()

wave_stream=obspy.Stream()
wave_trace= obspy.Trace()
wave_trace_rf= obspy.Trace()

# list all the files in the under the event folders
for f in event_folders:
    folders_event = os.path.join(source_path,f)
    file_paths = os.listdir(folders_event)
    for i in file_paths:
        if '.SAC' in i:
            #print(i)
            event_file = os.path.join(folders_event,i)
            split_1 = i.split(".")
            #print(split_1)
            staname = split_1[1]
            #print(staname)
            emp_event_name.add(f)
            emp_staname.add(staname)

emp_event_name = list(emp_event_name)
emp_staname = list(emp_staname)


print(emp_staname)
print(emp_event_name)

for f in event_folders:

    folders_event = os.path.join(source_path,f)
    file_paths = os.listdir(folders_event)

    # create event folder in the target path if it does not exist
    event_folder_target = os.path.join(target_path,f)
    if not os.path.exists(event_folder_target):
        os.makedirs(event_folder_target)

    # create 'GOOD' folder in the event folder if it does not exist
    event_folder_target_good = os.path.join(event_folder_target,'GOOD')
    if not os.path.exists(event_folder_target_good):
        os.makedirs(event_folder_target_good)

    for j in emp_staname:
        print(j)
        wave_stream.clear()
        for i in file_paths:
            if '.SAC' in i:
                if j in i:
                    #print(i)
                    event_file = os.path.join(folders_event,i)
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

        if len(wave_stream) != 3:
            continue

        for tr in wave_stream:
            station_name = tr.stats.station
            network_name = tr.stats.network
            distance = tr.stats.sac.dist
            comp = tr.stats.channel
            direc = comp[2]
            df = tr.stats.sampling_rate
            cft = recursive_sta_lta(tr, int(2.5 * df), int(10. * df))
            on_of = trigger_onset(cft, 3.5, 0.5)
            maximum = np.max(cft)
            max_ind = np.where(cft == maximum)
            maxval = max_ind[0]
            time = maxval / df
            time = time.astype(float)
            time = time[0]

            depth_meters = tr.stats.sac.evdp
            depth_km = depth_meters
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
            sampling_rate = st_TRZ[0].stats.sampling_rate
            print(sampling_rate)

            # gauss with floating point %3.1f
            gauss_str = '%3.1f' % gauss
            # file out name convention for radial : f{network_name}_{station_name}_{gauss_str}_i.r
            file_out_name_radial = f'{network_name}_{station_name}_{gauss_str}_i.r'
            file_out_name_trans = f'{network_name}_{station_name}_{gauss_str}_i.t'
            file_out_name_vert = f'{network_name}_{station_name}_{gauss_str}_i.z'
            
            # save the radial component
            file_out_path_radial = os.path.join(event_folder_target_good,file_out_name_radial)
            st_TRZ[1].write(file_out_path_radial,format='SAC')

            # save the transverse component
            file_out_path_trans = os.path.join(event_folder_target_good, file_out_name_trans)
            st_TRZ[2].write(file_out_path_trans,format='SAC')

            # save the vertical component
            file_out_path_vert = os.path.join(event_folder_target_good,file_out_name_vert)
            st_TRZ[0].write(file_out_path_vert,format='SAC')

            model = TauPyModel(model='ak135')
            arrivals = model.get_travel_times(ev_dep, dis, phase_list=['P'])
            
            if not arrivals:
                continue

            arr = arrivals[0]
            ray_parameter = arr.ray_param
            p_arrive_times = arr.time
            ray_incidence = arr.incident_angle

            window_maximum = p_arrive_times + window_length
            window_minimum = p_arrive_times - window_length

            rounded_start = round(window_minimum)
            rounded_end = round(window_maximum)

            possible_p_window_trig = cft[rounded_start:rounded_end]
            possible_p_window_trace = tr[rounded_start:rounded_end]
            print(possible_p_window_trig)

            rounded_start_ind = int(rounded_start * df)
            rounded_end_ind  = int(rounded_end * df)

            possible_p_window_trig = cft[rounded_start_ind:rounded_end_ind]


    subprocess.call(['./' + cut_name, event_folder_target],cwd=target_path)
    subprocess.call(['./' + decon_name, event_folder_target],cwd=target_path)

            
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
