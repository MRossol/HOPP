from defaults.pv_singleowner import PV_pvsingleowner, Singleowner_pvsingleowner
from defaults.wind_singleowner import wind_windsingleowner, singleowner_windsingleowner
from defaults.genericsystem_singleowner import genericsystem_genericsystemsingleowner, battery_genericsystemsingleowner, \
    singleowner_genericsystemsingleowner

Site = {
    'site': {
        "lat": 39.7555,
        "lon": -105.2211,
        "elev": 1879,
        "year": 2012,
        "tz": -7
    }
}

defaults = {
    'Site_boundaries': {
        'verts': [[3.0599999999976717, 288.87000000011176],
                    [0.0, 1084.0300000002608],
                    [1784.0499999999884, 1084.2400000002235],
                    [1794.0900000000256, 999.6399999996647],
                    [1494.3400000000256, 950.9699999997392],
                    [712.640000000014, 262.79999999981374],
                    [1216.9800000000396, 272.3600000003353],
                    [1217.7600000000093, 151.62000000011176],
                    [708.140000000014, 0.0]],
        'verts_simple': [[3.0599999999976717, 288.87000000011176],
                        [0.0, 1084.0300000002608],
                        [1784.0499999999884, 1084.2400000002235],
                        [1794.0900000000256, 999.6399999996647],
                        [1216.9800000000396, 272.3600000003353],
                        [1217.7600000000093, 151.62000000011176],
                        [708.140000000014, 0.0]]
    }
}