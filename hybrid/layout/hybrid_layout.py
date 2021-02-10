from typing import Optional
import numpy as np
from pathlib import Path
import os

from hybrid.power_source import PowerSource, SiteInfo
from hybrid.layout.wind_layout import WindLayout, WindBoundaryGridParameters
from hybrid.layout.solar_layout import SolarLayout, SolarGridParameters
from hybrid.layout.solar_layout_tools import get_flicker_loss_multiplier
from hybrid.layout.flicker_mismatch import FlickerMismatch


class HybridLayout:
    def __init__(self,
                 site: SiteInfo,
                 power_sources: dict,
                 flicker_load_nearest: bool = True):
        self.site: SiteInfo = site
        self.solar: Optional[SolarLayout] = None
        self.wind: Optional[WindLayout] = None
        for source, model in power_sources.items():
            if source == 'wind':
                self.wind = model._layout
            if source == 'solar':
                self.solar = model._layout

        self.is_hybrid = self.wind and self.solar
        self._flicker_data = None

        if self.is_hybrid:
            self._load_flicker_data(flicker_load_nearest)
            self.set_layout()

    def _load_flicker_data(self,
                           flicker_load_nearest: bool):
        """
        Try to load the file containing the flicker heat map of a single turbine for the lat, lon. This flicker heat
        map was generated separately using flicker_mismatch.py for a (lat, lon). It was computed with these settings:
            `diam_mult` identifies how many diameters to the left, right and above of the turbine is in the grid
                while 4 diameters to the bottom are inside the grid
            `flicker_diam` identifies the size of the turbine in the flicker model and how to scale the results to =
                turbines of different sizes
            `steps_per_hour` is the timestep interval of shadow calculation
            `angles_per_step` is how many different angles of the blades are calculated per timestep

        If not flicker_load_nearest, generate a low-resolution flicker heat map

        :return: tuple:
                    (turbine diameter,
                     tuple of turbine location x, y indices,
                     2-D array containing flicker loss multiplier at x, y coordinates (0-1, 0 is no loss),
                     x_coordinates of grid,
                     y_coordinates of grid)
        """
        if flicker_load_nearest:
            # pre-processed detailed flicker heat map
            existing_locations = [[33.209, -108.283],
                                  [36.334, -119.769],
                                  [39.7555, -105.2211]]
            current_location = [self.site.data['lat'], self.site.data['lon']]
            distance = np.array(existing_locations) - np.array(current_location)
            distance = np.linalg.norm(distance, axis=1)
            min_dist_location = existing_locations[int(np.argmin(distance))]
            flicker_diam = 70  # meters, of the turbine used in flicker modeling
            steps_per_hour = 4
            angles_per_step = 12
            data_path = Path(__file__).parent / "flicker_data"
            flicker_path = data_path / "{}_{}_{}_{}_shadow.txt".format(min_dist_location[0],
                                                                       min_dist_location[1],
                                                                       steps_per_hour, angles_per_step)
            flicker_heatmap = np.loadtxt(flicker_path)

            bounds = FlickerMismatch.get_turb_site(flicker_diam).bounds
            _, heatmap_template = FlickerMismatch._setup_heatmap_template(bounds)
        else:
            flicker_diam = self.wind.rotor_diameter
            flicker_no_tower = FlickerMismatch(self.site.data['lat'], self.site.data['lon'],
                                               blade_length=flicker_diam // 2,
                                               angles_per_step=None,
                                               gridcell_height=90, gridcell_width=90, gridcells_per_string=1)

            (flicker_heatmap,) = flicker_no_tower.create_heat_maps(range(8760), ("power",))
            heatmap_template = flicker_no_tower.heat_map_template

        turb_x_ind, turb_y_ind = FlickerMismatch.get_turb_pos_indices(heatmap_template)
        return flicker_diam, (turb_x_ind, turb_y_ind), flicker_heatmap, heatmap_template[1], heatmap_template[2]

    def calculate_flicker_loss(self):
        # get solar capacity after flicker losses
        net_solar_capacities = []
        flicker_losses = 1
        for area in self.solar.solar_region:
            solar_capacity = self.solar.module_power * area.num_modules
            # gcr_loss = self.solar_gcr_loss_multiplier(area.gcr)
            # solar_capacity *= gcr_loss
            flicker_loss = get_flicker_loss_multiplier(self._flicker_data,
                                                       self.wind.turb_pos_x,
                                                       self.wind.turb_pos_y,
                                                       self.wind.rotor_diameter,
                                                       area.strands,
                                                       (self.solar.module_width, self.solar.module_height))
            solar_capacity *= flicker_loss
            flicker_losses *= flicker_loss
            net_solar_capacities.append(solar_capacity)

        total_solar_capacity = sum(net_solar_capacities)
        if total_solar_capacity == 0:
            return 0

    def reset_layout(self,
                     wind_params: Optional[WindBoundaryGridParameters],
                     solar_params: Optional[SolarGridParameters]):
        if self.solar:
            self.solar.set_layout_params(solar_params)

        if self.wind:
            if not self.is_hybrid:
                self.wind.set_layout_params(wind_params)
            else:
                # exclusion solar panels area from the wind placement
                self.wind.set_layout_params(wind_params, self.solar.buffer_region)

            # calculate flicker loss

    def set_layout(self):
        solar_params = None
        wind_params = None
        if self.solar:
            solar_params = self.solar.parameters
        if self.wind:
            wind_params = self.wind.parameters

        self.reset_layout(wind_params, solar_params)

    def plot(self,
             figure=None,
             axes=None,
             wind_color='b',
             solar_color='darkorange',
             site_border_color='k',
             alpha=0.95,
             linewidth=4.0
             ):
        if not figure or not axes:
            figure, axes = self.site.plot(figure, axes, site_border_color, alpha, linewidth)
        if self.wind:
            self.wind.plot(figure, axes, wind_color, site_alpha=alpha)
        if self.solar:
            self.solar.plot(figure, axes, solar_color, site_alpha=alpha)
        return figure, axes