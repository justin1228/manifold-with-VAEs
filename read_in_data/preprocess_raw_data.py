'''March 27th 2019
Script to preprocess raw data.
The option make_processed_files takes the downloaded files and
accumulates spikes, angles and state information into a single
Python friendly structure.
The option make_rates takes the file generated by make_processed_files
and computes rate estimates from the spike timings.
'''

from __future__ import division
import numpy as np
import numpy.linalg as la
import sys, os
import time, datetime
import pandas as pd
import re

gen_fn_dir = os.path.abspath('..') + '/shared_scripts'
sys.path.append(gen_fn_dir)
import general_file_fns as gff
import data_read_fns as drf
import rate_functions as rf


def is_session(fname):
    p = re.compile(r'Mouse\d\d-\d\d\d\d\d\d$')
    result = True if p.match(fname) else False
    return result


# Paths to save the data are in this dict. If you haven't already, edit
# general_params/make_general_params_file.py to set the paths you want
# and run it to generate general_params.p


gen_params = gff.load_pickle_file('../general_params/general_params.p')
make_processed_files = False
make_rates = False
print_rates_data = False
print_preprocessed_data = True


data_path = gen_params['raw_data_dir'] + '/'
folder_list = os.listdir(data_path)
print(folder_list)
session_list = [x for x in folder_list if is_session(x)]
print(session_list)


if make_processed_files:
    for session in session_list:
        data_path = gen_params['raw_data_dir'] + session + '/'
        params = {'session': session, 'data_path': data_path,
                  'eeg_sampling_rate': 1250., 'spike_sampling_interval': 1.0 / 20e3}
        if os.path.isfile(gen_params['processed_data_dir'] + '%s.p' % session):  # preprocessing 중복 방지(시간 절약)
            continue
        print(session)
        data = drf.gather_session_spike_info(params)
        save_dir = gff.return_dir(gen_params['processed_data_dir'])
        gff.save_pickle_file(data, save_dir + '%s.p' % session)

if make_rates:
    for session in session_list:
        print('Getting kernel rates for ' + session)
        t0 = time.time()
        sigma = 0.1
        params = {'dt': 0.05, 'method': 'gaussian', 'sigma': sigma}  # Parameter time_interval=50ms
        save_dir = gff.return_dir(
            gen_params['kernel_rates_dir'] + '%0.0fms_sigma/' % (sigma * 1000))

        inp_data = gff.load_pickle_file(gen_params['processed_data_dir'] +
                                        '%s.p' % session)

        rates = rf.get_rates_and_angles_by_interval(inp_data, params, smooth_type='kernel',
                                                    just_wake=True)

        gff.save_pickle_file(rates, save_dir + '%s.p' % session)
        print('Time ', time.time() - t0)

if print_rates_data:
    sys.stdout = open('preprocess_rates.txt', 'w')
    for session in session_list:
        print("**************************************************************************")
        print('Printing Wake kernel rates data ' + session)
        sigma = 0.1
        inp_data = gff.load_pickle_file(gen_params['kernel_rates_dir'] +
                                        '%0.0fms_sigma/' % (sigma * 1000) + '%s.p' % session)
        states = inp_data.keys()
        # print(states)
        for state in states:
            if state == "Wake":
                for tmp_interval in inp_data["Wake"]:
                    interval = tuple(tmp_interval)
                    print(inp_data[state][interval].keys())
                    print(" State: ", state, "\n", "Interval: ", interval)
                    print("RATES: ")
                    kernel_rates = pd.DataFrame.from_dict(inp_data[state][interval]['rates'], orient='index')
                    print(kernel_rates)
                    print("_______________________________________________________________________")
                    rate_times = pd.DataFrame.from_dict(inp_data[state][interval]['rate_times'])
                    print(rate_times)
                    print("_______________________________________________________________________")
                    print("ANGLES: ")
                    angles = pd.DataFrame.from_dict(inp_data[state][interval]['angles'])
                    print(angles)
                    print("_______________________________________________________________________")
                    print("ANGLE_TIMES: ")
                    angle_times = pd.DataFrame.from_dict(inp_data[state][interval]['angle_times'])

    sys.stdout.close()

if print_preprocessed_data:
    # sys.stdout = open('processed.txt', 'w')
    for session in session_list:
        print("**************************************************************************")
        print("Printing Processed data " + session)
        processed_data = gff.load_pickle_file(gen_params['processed_data_dir'] + '%s.p' % session)
        print(processed_data.keys())
        print(processed_data['pos_sampling_rate'])
        print("\n")
    # sys.stdout.close()
