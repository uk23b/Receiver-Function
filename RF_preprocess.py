
from multiprocessing import Event
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
import pandas as pd
import seispy


target_freq = 10
model = TauPyModel(model='iasp91')

shift = 5
time_after = 60

# create pandas dataframe
df = pd.DataFrame(columns=['Event_Year','Event_Julday','Event_Hour','Event_Min','Event_Sec',
                            'Station_Name','Sta_lat','Sta_lon','Sta_Elevation',
                            'Event_Lat','Event_Lon','Event_Depth','Event_Mag',
                            'P_arrival_time','S_arrival_time','P_S_diff',
                            'Rotated_Component','Network','Distance','SNR'])



#####  parameters ######

# window length for P wave detection by using STA_LTA. 
# Reference time is based on TauP traveltime curve
sta_lta_window = 10



window_length = 30 #seconds
max_filt = 1  #minimum end of bandpass filter (Hz)
min_filt = 0.2 #maximum end of bandpass filter (Hz)


m = open('sta_lta_out.txt', 'w')


target_path = r'/Volumes/UNTITLE/09_decon_iter/'


year = 'test'
source_path = r'/Volumes/UNTITLE/03_extract_event/RF_events/'
#source_path = r'/Volumes/UNTITLED/06_STA_LTA/temp/'
year_events = os.path.join(source_path,year)

emp_event_name = set()
emp_staname = set()

wave_stream=obspy.Stream()
wave_trace= obspy.Trace()

wave_trace_rf= obspy.Trace()
wave_trace_rf_ALL = obspy.Trace()


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

                # fs of the data
                fs = st[0].stats.sampling_rate
                # create decimation factor for downsampling to 10 Hz

                dec_fac = int(fs/target_freq)
                # decimate data
                st.decimate(dec_fac)
                
                if len(st) == 0:
                    continue
                
                st._trim_common_channels()
                st.trim(max(tr.stats.starttime for tr in st), min(tr.stats.endtime for tr in st))
                wave_stream += st

        wave_stream.sort(keys=['channel'], reverse = True)

        # create a train.csv and test.csv file for each station
        df = pd.DataFrame(columns=['Event_Year','Event_Julday','Event_Hour','Event_Min','Event_Sec',
                            'Station_Name','Sta_lat','Sta_lon','Sta_Elevation',
                            'Event_Lat','Event_Lon','Event_Depth','Event_Mag',
                            'P_arrival_time','S_arrival_time','P_S_diff',
                            'Component','Network','Distance','ArcDist','SNR',
                            'time_series_x_point', 'time_series_y_point', 'series_id'])

        if len(wave_stream) == 3:
            wave_stream[0].data = wave_stream[0].data.astype(np.float32)
            wave_stream[1].data = wave_stream[1].data.astype(np.float32)
            wave_stream[2].data = wave_stream[2].data.astype(np.float32)

            #print('length of wave stream is ', (wave_stream[0].stats.endtime - wave_stream[0].stats.starttime))
            # create sample points

            #x_time_series_1 = np.arange(0, (wave_stream[0].stats.endtime - wave_stream[0].stats.starttime), 1/target_freq)
            # y time series is the data (amplitude)
            #y_time_series_1 = wave_stream[0].data

            Event_Year_1 = wave_stream[0].stats.starttime.year
            Event_Julday_1 = wave_stream[0].stats.starttime.julday
            Event_Hour_1 = wave_stream[0].stats.starttime.hour
            Event_Min_1 = wave_stream[0].stats.starttime.minute
            Event_Sec_1 = wave_stream[0].stats.starttime.second
            Station_Name_1 = wave_stream[0].stats.station
            Sta_lat_1 = wave_stream[0].stats.sac.stla
            Sta_lon_1 = wave_stream[0].stats.sac.stlo
            Sta_Elevation_1 = wave_stream[0].stats.sac.stel
            Event_Lat_1 = wave_stream[0].stats.sac.evla
            Event_Lon_1 = wave_stream[0].stats.sac.evlo
            Event_Depth_1 = wave_stream[0].stats.sac.evdp
            Event_Mag_1 = wave_stream[0].stats.sac.user8
            Component_1 = wave_stream[0].stats.channel
            Network_1 = wave_stream[0].stats.network
            Distance_1 = wave_stream[0].stats.sac.dist
            ArcDist_1 = wave_stream[0].stats.sac.gcarc

            wave_trace_rf_1 = wave_stream[0]

            wave_trace_rf_1.detrend()
            wave_trace_rf_1.filter("bandpass", freqmin=0.05, freqmax=2.0, zerophase=True)
            wave_trace_rf_1.plot(show=False)

            da_1 = seispy.distaz(Sta_lat_1, Sta_lon_1, Event_Lat_1, Event_Lon_1)
            bazi = da_1.baz
            ev_dep = Event_Depth_1
            print('back-azimuth = %5.2f˚' % bazi)

            arrivals_1 = model.get_travel_times(source_depth_in_km=ev_dep, distance_in_degree=ArcDist_1, phase_list=["P", "S"])

            if not arrivals_1:
                continue
                
            arr_P_1 = arrivals_1[0]
            arr_S_1 = arrivals_1[1]





            #x_time_series_2 = np.arange(0, (wave_stream[1].stats.endtime - wave_stream[1].stats.starttime), 1/target_freq)
            # y time series is the data (amplitude)
            #y_time_series_2 = wave_stream[1].data

            Event_Year_2 = wave_stream[1].stats.starttime.year
            Event_Julday_2 = wave_stream[1].stats.starttime.julday
            Event_Hour_2 = wave_stream[1].stats.starttime.hour
            Event_Min_2 = wave_stream[1].stats.starttime.minute
            Event_Sec_2 = wave_stream[1].stats.starttime.second
            Station_Name_2 = wave_stream[1].stats.station
            Sta_lat_2 = wave_stream[1].stats.sac.stla
            Sta_lon_2 = wave_stream[1].stats.sac.stlo
            Sta_Elevation_2 = wave_stream[1].stats.sac.stel
            Event_Lat_2 = wave_stream[1].stats.sac.evla
            Event_Lon_2 = wave_stream[1].stats.sac.evlo
            Event_Depth_2 = wave_stream[1].stats.sac.evdp
            Event_Mag_2 = wave_stream[1].stats.sac.user8
            Component_2 = wave_stream[1].stats.channel
            Network_2 = wave_stream[1].stats.network
            Distance_2 = wave_stream[1].stats.sac.dist
            ArcDist_2 = wave_stream[1].stats.sac.gcarc

            wave_trace_rf_2 = wave_stream[1]

            wave_trace_rf_2.detrend()
            wave_trace_rf_2.filter("bandpass", freqmin=0.05, freqmax=2.0, zerophase=True)
            wave_trace_rf_2.plot(show=False)

            da_2 = seispy.distaz(Sta_lat_2, Sta_lon_2, Event_Lat_2, Event_Lon_2)
            bazi = da_2.baz
            ev_dep = Event_Depth_2
            print('back-azimuth = %5.2f˚' % bazi)

            arrivals_2 = model.get_travel_times(source_depth_in_km=ev_dep, distance_in_degree=ArcDist_2, phase_list=["P", "S"])



            #x_time_series_3 = np.arange(0, (wave_stream[2].stats.endtime - wave_stream[2].stats.starttime), 1/target_freq)
            # y time series is the data (amplitude)
            #y_time_series_3 = wave_stream[2].data

            Event_Year_3 = wave_stream[2].stats.starttime.year
            Event_Julday_3 = wave_stream[2].stats.starttime.julday
            Event_Hour_3 = wave_stream[2].stats.starttime.hour
            Event_Min_3 = wave_stream[2].stats.starttime.minute
            Event_Sec_3 = wave_stream[2].stats.starttime.second
            Station_Name_3 = wave_stream[2].stats.station
            Sta_lat_3 = wave_stream[2].stats.sac.stla
            Sta_lon_3 = wave_stream[2].stats.sac.stlo
            Sta_Elevation_3 = wave_stream[2].stats.sac.stel
            Event_Lat_3 = wave_stream[2].stats.sac.evla
            Event_Lon_3 = wave_stream[2].stats.sac.evlo
            Event_Depth_3 = wave_stream[2].stats.sac.evdp
            Event_Mag_3 = wave_stream[2].stats.sac.user8
            Component_3 = wave_stream[2].stats.channel
            Network_3 = wave_stream[2].stats.network
            Distance_3 = wave_stream[2].stats.sac.dist
            ArcDist_3 = wave_stream[2].stats.sac.gcarc

            wave_trace_rf_3 = wave_stream[2]

            wave_trace_rf_3.detrend()
            wave_trace_rf_3.filter("bandpass", freqmin=0.05, freqmax=2.0, zerophase=True)
            wave_trace_rf_3.plot(show=False)

            da_3 = seispy.distaz(Sta_lat_3, Sta_lon_3, Event_Lat_3, Event_Lon_3)
            bazi = da_3.baz
            ev_dep = Event_Depth_3
            print('back-azimuth = %5.2f˚' % bazi)

            arrivals_3 = model.get_travel_times(source_depth_in_km=ev_dep, distance_in_degree=ArcDist_3, phase_list=["P", "S"])




            #trim the data to have the same time span for rotation from NE to RT
            wave_stream.trim(max(tr.stats.starttime for tr in wave_stream), min(tr.stats.endtime for tr in wave_stream))
            st_TRZ = wave_stream.copy().rotate('NE->RT', back_azimuth=bazi)
            st_TRZ.plot(show=False)
            x_time_series_Z = np.arange(0, (st_TRZ[0].stats.endtime - st_TRZ[0].stats.starttime), 1/target_freq)
            y_time_series_Z = st_TRZ[0].data

            x_time_series_R = np.arange(0, (st_TRZ[1].stats.endtime - st_TRZ[1].stats.starttime), 1/target_freq)
            y_time_series_R = st_TRZ[1].data

            x_time_series_T = np.arange(0, (st_TRZ[2].stats.endtime - st_TRZ[2].stats.starttime), 1/target_freq)
            y_time_series_T = st_TRZ[2].data

            arr_P_1 = arrivals_1[0]
            print(arr_P_1)

            st_TRZI=st_TRZ.decimate(1, strict_length=False, no_filter=True)
            st_TRZI=st_TRZI.trim(st_TRZI[0].stats.starttime+arr_P_1.time-shift, st_TRZI[0].stats.starttime+arr_P_1.time+time_after)
            st_TRZI.plot(show=False)
            #print(len(st_TRZI[0].data))
            rf = deconiti(uin=st_TRZI[1], win=st_TRZI[0], dt=st[0].stats.delta, nt=None, tshift=5, f0=2, itmax=400, minderr=0.001, phase='P')
            print(type(rf))
            wave_trace_rf_ALL = obspy.Trace()
            wave_trace_rf_ALL.data = rf[0]
            time_axis = st_TRZI[0].times() - shift

            file_rf_name = f+'_'+ Station_Name_1 + '_RF_P' + '.sac'
            filename_sac = f+'_'+ Station_Name_1 + '_RF_P' + '.sac'

            plt.plot(time_axis,rf[0])
            #plt.show()
            sta_out_folder = os.path.join(target_path,'done')
            sta_out_folder_stations = os.path.join(sta_out_folder,j)
            if not os.path.exists(sta_out_folder_stations):
                os.makedirs(sta_out_folder_stations)

            out_rf_filepath = os.path.join(sta_out_folder_stations,file_rf_name)
            out_rf_filepath_sac = os.path.join(sta_out_folder_stations,filename_sac)

            

            # df = pd.DataFrame({'Event_Year': [Event_Year_1], 'Event_Julday': [Event_Julday_1], 'Event_Hour': [Event_Hour_1], 'Event_Min': [Event_Min_1], 'Event_Sec': [Event_Sec_1], 
            # 'Station_Name': [Station_Name_1], 'Sta_lat': [Sta_lat_1], 'Sta_lon': [Sta_lon_1], 'Sta_Elevation': [Sta_Elevation_1], 'Event_Lat': [Event_Lat_1], 'Event_Lon': [Event_Lon_1], 'Event_Depth': [Event_Depth_1], 'Event_Mag': [Event_Mag_1], 
            # 'Component': [Component_1], 'Network': [Network_1], 'Distance': [Distance_1], 'ArcDist': [ArcDist_1], 
            # 'Event_Year_2': [Event_Year_2], 'Event_Julday_2': [Event_Julday_2], 'Event_Hour_2': [Event_Hour_2], 'Event_Min_2': [Event_Min_2], 'Event_Sec_2': [Event_Sec_2], 
            # 'Station_Name_2': [Station_Name_2], 'Sta_lat_2': [Sta_lat_2], 'Sta_lon_2': [Sta_lon_2], 'Sta_Elevation_2': [Sta_Elevation_2], 'Event_Lat_2': [Event_Lat_2], 'Event_Lon_2': [Event_Lon_2], 'Event_Depth_2': [Event_Depth_2], 'Event_Mag_2': [Event_Mag_2], 
            # 'Component_2': [Component_2], 'Network_2': [Network_2], 'Distance_2': [Distance_2], 'ArcDist_2': [ArcDist_2], 'Event_Year_3': [Event_Year_3], 'Event_Julday_3': [Event_Julday_3], 'Event_Hour_3': [Event_Hour_3], 'Event_Min_3': [Event_Min_3], 'Event_Sec_3': [Event_Sec_3], 
            # 'Station_Name_3': [Station_Name_3], 'Sta_lat_3': [Sta_lat_3], 'Sta_lon_3': [Sta_lon_3], 'Sta_Elevation_3': [Sta_Elevation_3], 'Event_Lat_3': [Event_Lat_3], 'Event_Lon_3': [Event_Lon_3], 'Event_Depth_3': [Event_Depth_3], 'Event_Mag_3': [Event_Mag_3],
            # 'Component_3': [Component_3], 'Network_3': [Network_3], 'Distance_3': [Distance_3], 'ArcDist_3': [ArcDist_3]})


#             wave_trace_rf_ALL.write(out_rf_filepath_sac,format='SAC')
#             plt.xlim(-shift, time_after + shift)
#             plt.ylim(-1, 1)
#             plt.savefig(out_rf_filepath)

#             wave_stream.clear()
#             st_TRZ.clear()
#             st_TRZI.clear()
#             st.clear()
#             plt.clf()
#             plt.cla()

#         gc.collect()
#         plt.close('all')


# m.close()
# print('done')





            

        # # length of the data
        # npts = wave_stream[0].stats.npts
        # print('length of the data is ', npts)


                            

        

