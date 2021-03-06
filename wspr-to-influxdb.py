#!/usr/bin/python
'''
This module does prepare and upload the ALL_WSPR.TXT-format to the influxdb-server

Author : PA7T Clemens Heese clemens at pa7t.nl
         DK5HH Michael Hartje DK5HH at darc.de

Installation:
Prepare the python installation depending on what python version you are
using (2/3)
we need to add the modules in addition to a standeard python installation
influxdb
pyhamtools
geohash
You can install these modules with for pythoon 2 with
pip2 install modulename
or for python 3 with
pip3 install modulename

check the installtion in python console
import modulename
(no answer is good news.)

'''


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    Bearing=atan2(sin(dlon)*cos(lat2),
                  cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(dlon))/pi*180
    if Bearing < 0:
        Bearing+=360
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return int(km), int(Bearing)


def wspr_to_file(in_str,wspr_reporter,wspr_loc_reporter, fout):

    # implemented for legacy compatibility
    # in_str = '160310 1942   1 -24 -4.0  7.0395714  PA2W JO22 37            1  6739  -48'

    in_str = in_str.replace('     ', ' ')
    in_str = in_str.replace('    ', ' ')
    in_str = in_str.replace('   ', ' ')
    in_str = in_str.replace('  ', ' ')

    wspr_date, wspr_time, wspr_other, wspr_snr, wspr_dt, wspr_freq, wspr_call, wspr_loc, wspr_pwr, wspr_drift, wspr_rest = in_str.split(
        ' ', 10)

    band_vec = ('LF', 'MW', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m', '12m', '10m')
    freq_vec = (0.1, 0.4, 1.8, 3.5, 5.2, 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.1)
    wspr_band = band_vec[freq_vec.index(round(float(wspr_freq) - 0.05, 1))]

    wspr_tuple_time = strptime(wspr_date + wspr_time, "%y%m%d%H%M")
    wspr_time = strftime("%Y-%m-%dT%H:%M:%SZ", wspr_tuple_time)

    loclon_reporter = mlocs.toLoc(wspr_loc_reporter)
    wspr_geohash_reporter = Geohash.encode(loclon_reporter[0], loclon_reporter[1], precision=7)

    calckm_az = False
    if wspr_call.find('/') < 0 or wspr_call.find('<') == 0:
        calckm_az = True

    else:
        wspr_dist = -1
        wspr_az = -1
        wspr_drift = wspr_pwr
        wspr_pwr = wspr_loc
        wspr_loc = 'AA00'
        wspr_geohash = '0000'

    if wspr_call.find('<') == 0:
        wspr_call = wspr_call[1:-1]
        if wspr_call.find('..') >= 0:
            wspr_call = "00" + wspr_loc

    wspr_call = re.sub('[<>]', '', wspr_call)

    if wspr_call.find('..') >= 0:
        wspr_call = "00" + wspr_loc

    if calckm_az:
        loclon = mlocs.toLoc(wspr_loc)
        wspr_dist, wspr_az = haversine(loclon_reporter[0], loclon_reporter[1], loclon[0], loclon[1])
        wspr_geohash = Geohash.encode(loclon[0], loclon[1], precision=7)

    dat_str_local = 'wspr_redpitaya' + ',reporter=' + str(wspr_reporter) + \
                    ',call=' + wspr_call + ',band=' + str(wspr_band).rjust(4, '.') + \
                    ',loc=' + wspr_loc + \
                    ',geohash=' + str(wspr_geohash) + ',geohash_reporter=' + str(wspr_geohash_reporter) + \
                    ' snr=' + str(wspr_snr) + ',freq=' + str(wspr_freq) + ',drift=' + str(wspr_dt) + \
                    ',dist=' + str(wspr_dist) + ',az=' + str(wspr_az) + \
                    ',bandi=' + str(wspr_band) + \
                    ',pwr=' + str(wspr_pwr) + ' ' + str(wspr_time)


    fout.write(dat_str_local + '\n')


def wspr_to_json(in_str,wspr_reporter,wspr_loc_reporter):

    # in_str = '160310 1942   1 -24 -4.0  7.0395714  PA2W JO22 37            1  6739  -48'

    in_str = in_str.replace('     ', ' ')
    in_str = in_str.replace('    ', ' ')
    in_str = in_str.replace('   ', ' ')
    in_str = in_str.replace('  ', ' ')

    wspr_date, wspr_time, wspr_other, wspr_snr, wspr_dt, wspr_freq, wspr_call, wspr_loc, wspr_pwr, wspr_drift, wspr_rest = in_str.split(' ', 10)

    band_vec = ('LF', 'MW', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m', '12m', '10m')
    freq_vec = (0.1, 0.4, 1.8, 3.5, 5.2, 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.1)
    wspr_band = band_vec[freq_vec.index(round(float(wspr_freq) - 0.05, 1))]

    wspr_tuple_time = strptime(wspr_date + wspr_time, "%y%m%d%H%M")
    wspr_time = strftime("%Y-%m-%dT%H:%M:%SZ", wspr_tuple_time)

    loclon_reporter = mlocs.toLoc(wspr_loc_reporter)
    wspr_geohash_reporter = Geohash.encode(loclon_reporter[0], loclon_reporter[1], precision=7)

    calckm_az = False
    if wspr_call.find('/') < 0 or wspr_call.find('<') == 0:
        calckm_az = True

    else:
        wspr_dist = -1
        wspr_az = -1
        wspr_drift = wspr_pwr
        wspr_pwr = wspr_loc
        wspr_loc = 'AA00'
        wspr_geohash = '0000'

    if wspr_call.find('<') == 0:
        wspr_call = wspr_call[1:-1]
        if wspr_call.find('..') >= 0:
            wspr_call = "00" + wspr_loc

    wspr_call = re.sub('[<>]', '', wspr_call)

    if wspr_call.find('..') >= 0:
        wspr_call = "00" + wspr_loc

    if calckm_az:
        loclon = mlocs.toLoc(wspr_loc)
        wspr_dist, wspr_az = haversine(loclon_reporter[0], loclon_reporter[1], loclon[0], loclon[1])
        wspr_geohash = Geohash.encode(loclon[0], loclon[1], precision=7)



    json_body = [
        {
            "measurement": "wspr_redpitaya_test",
            "tags": {
                "reporter": wspr_reporter,
                "call": wspr_call,
                "band": str(wspr_band).rjust(4,'.'),
                "loc": wspr_loc,
                "loc_reporter": wspr_loc_reporter,
                "geohash": wspr_geohash,
                "geohash_reporter": wspr_geohash_reporter
            },
            "time": wspr_time,
            "fields": {
                "snr": int(float(wspr_snr)),
                "freq": float(wspr_freq),
                "drift": int(float(wspr_drift)),
                "dist": wspr_dist,
                "az": wspr_az,
                "bandi": wspr_band,
                "pwr": int(float(wspr_pwr))
            }
        }
    ]
    return json_body

if __name__ == '__main__':  # noqa
    import re
    from time import strftime, strptime
    from math import radians, cos, sin, asin, sqrt, atan2, pi
    from influxdb import InfluxDBClient
    import argparse
    import mlocs
    import Geohash

    parser = argparse.ArgumentParser(
        description='Load ALL_WSPR.TXT like file to Influxdb',
        epilog="""... epilog ... no more info atm ...""")

    group = parser.add_argument_group('files')

    parser.add_argument(
        '-fi',
        type=str,
        help="filename of ALL_WSPR.TXT-file",
        default='ALL_WSPR.TXT')

    parser.add_argument(
        '-r', '--reporter',
        type=str,
        help="Reporter call sign",
        default='PA7T')

    parser.add_argument(
        '-rl', '--reporter-locator',
        type=str,
        help="Reporter locator",
        default='JO22FD')

    parser.add_argument('-fo',
        type=str,
        help="filename to output",
        default=False)

    args = parser.parse_args()
    # try to open input file
    try:
        f = open(args.fi, "r")
    except (IOError, OSError):
        print "Error: Cannot open file {} for reading!\n".format(args.fi)
        exit(1)
    else:
        print "Processing file {} ...\n".format(args.fi)
        try:
            if args.fo:
                fout = open(args.fo,'a')
                print "Additional output to {}.\n".format(args.fo)
            # open connection to Influxdb
            client = InfluxDBClient('thehost.home.net', 8087, 'user_name', 'secret_password', 'wspr')
            # iterate over lines
            wspr_no = sum(1 for line in f)
            f.seek(0, 0)
            i=0
            for in_str in f:
                print "{}/{}".format(i,wspr_no-1)
                #print(in_str)
                json_body = wspr_to_json(in_str,args.reporter,args.reporter_locator)
                #print(json_body)

                if args.fo:
                    wspr_to_file(in_str, args.reporter, args.reporter_locator, fout)
                else:
                    # submit spot to Influxdb
                    ret = client.write_points(json_body)
                i=i+1
            print("\nDone.")
        finally:
            f.close()
            if args.fo:
                fout.close()

