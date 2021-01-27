from pathlib import Path
import matplotlib.pyplot as plt
from hybrid.sites import make_circular_site, make_irregular_site, SiteInfo, locations
from hybrid.hybrid_simulation import HybridSimulation
from hybrid.layout import WindBoundaryGridParameters

site = 'irregular'
location = locations[1]
site_data = None

if site == 'circular':
    site_data = make_circular_site(lat=location[0], lon=location[1], elev=location[2])
elif site == 'irregular':
    site_data = make_irregular_site(lat=location[0], lon=location[1], elev=location[2])
else:
    raise Exception("Unknown site '" + site + "'")

g_file = Path(__file__).parent.parent.parent / "resource_files" / "grid" / "pricing-data-2015-IronMtn-002_factors.csv"

site_info = SiteInfo(site_data, grid_resource_file=g_file)

# set up hybrid simulation with all the required parameters
solar_size_mw = 100
interconnection_size_mw = 150

technologies = {'solar': solar_size_mw,  # mw system capacity
                'wind': {
                    'num_turbines': 50,
                    'turbine_rating_kw': 2000,
                    'layout_mode': 'boundarygrid',
                    'params': WindBoundaryGridParameters(2, 0.5, 0.5, 0.5, 0.5)
                },
                'grid': interconnection_size_mw}

# Get resource

# Create model
hybrid_plant = HybridSimulation(technologies, site_info, interconnect_kw=interconnection_size_mw * 1000)
hybrid_plant.wind.layout.plot()
plt.show()
## sizes

## simple PV ROM -> low priority

## layout has many assumptions and constraints, as well as flicker data
### move turbines within boundary
### parameters to candidate -> returns penalties / or differences
### plotting features

# determine what set of parameters to modify and the objective function as func of Hybrid Sim instance

## modifying layout

# create the optimization problems

## Variables and prior distributions, clamp parameter range

## where do the penalties live?

# run the optimizerdriver

## layer between hybrid variables and hooks into hybrid simulation class, checking for existant attrs
## check constraints? calculate penalties?