#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module is used to compute a grid containing drawing of disks of stars,
planets and atmospheres.
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.special import voigt_profile
from PIL import Image, ImageDraw
from p_winds import tools

__all__ = ["draw_transit", "transmission"]


# Draw a grid
def draw_transit(planet_to_star_ratio, impact_parameter=0.0, phase=0.0,
                 grid_size=1001, density_profile=None, profile_radius=None,
                 planet_physical_radius=None):
    """

    Parameters
    ----------
    planet_to_star_ratio (``float``):
        Ratio between the radii of the planet and the star.

    impact_parameter (``float``, optional):
        Transit impact parameter. Default is 0.0.

    phase (``float``, optional):
        Phase of the transit. -0.5, 0.0, and +0.5 correspond to the center of
        planet being located at, respectively, the left limb of the star, the
        center, and the right limb. Default is 0.0.

    grid_size (``int``, optional):
        Size of the transit grid. Default is 2001.

    density_profile (``numpy.ndarray``, optional):
        1-D profile of volumetric number densities in function of radius. Unit
        has to be 1 / length ** 3, where length is the unit of
        ``planet_physical_radius``. If ``None``, the returned column densities
        will be zero. Default is ``None``.

    profile_radius (``numpy.ndarray``, optional):
        1-D profile of radii in which the densities are sampled. Unit
        has to be the same as ``planet_physical_radius``. Required if you want
        to calculate the map of column densities. Default is ``None``.

    planet_physical_radius (``float``, optional):
        Physical radius of the planet in whatever unit you want to work with.
        Required to calculate the map of column densities. Default is ``None``.

    Returns
    -------
    normalized_flux_map (``numpy.ndarray``):
        2-D map of fluxes normalized in such a way that the sum of the array
        will be 1.0 if the planet is not transiting.

    density_map (``numpy.ndarray``):
        2-D map of column densities in unit of 1 / length ** 2, where length is
        the unit of ``planet_physical_radius``.
    """
    shape = (grid_size, grid_size)

    # General function to draw a disk
    def _draw_disk(center, radius, value=1.0):
        """

        Parameters
        ----------
        center:
            Coordinates of the center of the disk. The origin is the center of the
            grid.

        radius:
            Radius of the disk in units of grid pixels.

        value:
            Value to be attributed to each pixel inside the disk.

        Returns
        -------

        """
        top_left = (center[0] - radius, center[1] - radius)
        bottom_right = (center[0] + radius, center[1] + radius)
        image = Image.new('1', shape)
        draw = ImageDraw.Draw(image)
        draw.ellipse([top_left, bottom_right], outline=1, fill=1)
        disk = np.reshape(np.array(list(image.getdata())), shape) * value
        return disk

    # Draw the host star
    star_radius = grid_size // 2
    planet_radius = star_radius * planet_to_star_ratio
    star = _draw_disk(center=(star_radius, star_radius), radius=star_radius)
    norm = np.sum(star)  # Normalization factor is the total flux
    # Adding the star to the grid
    grid = star / norm

    # Before drawing the planet, we will need to figure out the exact coordinate
    # of the center of the planet and then draw the cloud
    x_p = grid_size // 2 + int(phase * grid_size)
    y_p = grid_size // 2 + int(impact_parameter * grid_size // 2)

    # Add the upper atmosphere if a density profile was input
    if density_profile is not None:
        # We need to know the matrix r_p containing distances from
        # planet center when we draw the extended atmosphere
        one_d_coords = np.linspace(0, grid_size - 1, grid_size, dtype=int)
        x_s, y_s = np.meshgrid(one_d_coords, one_d_coords)
        planet_centric_coords = np.array([x_s - x_p, y_s - y_p]).T
        # We also need to know the physical size of the pixel in the grid
        px_size = planet_physical_radius / planet_radius
        r_p = (np.sum(planet_centric_coords ** 2, axis=-1) ** 0.5).T * px_size
        # Calculate the column densities profile
        column_density = 2 * np.sum(np.array([density_profile,
                                              density_profile]), axis=0)
        # In order to calculate the column density in a given pixel, we need to
        # interpolate from the array above based on the radius map
        f = interp1d(profile_radius, column_density, bounds_error=False,
                     fill_value=0.0)
        density_map = f(r_p)
    else:
        density_map = np.zeros_like(grid)

    # Finally
    planet = _draw_disk(center=(x_p, y_p), radius=planet_radius)
    # Adding the planet to the grid, normalized by the stellar flux
    grid -= planet / norm
    # The grid must not have negative values (this may happen if the planet
    # disk falls out of the stellar disk)
    normalized_flux_map = grid.clip(min=0.0)

    return normalized_flux_map, density_map


# Transmission profile in a gas cell
def transmission(cell_density, cell_temperature, oscillator_strength,
                 einstein_coeff, wavelength_grid, reference_wavelength,
                 particle_mass):
    """
    Calculate the transmission profile in a wavelength grid.

    Parameters
    ----------
    cell_density (``float``):
        Cell column or volumetric gas density in 1 / m ** 2 or 1 / m ** 3.

    cell_temperature (``float``):
        Cell gas temperature in K.

    oscillator_strength (``float``):
        Oscillator strength of the transition.

    einstein_coeff (``float``):
        Einstein coefficient of the transition in 1 / s.

    wavelength_grid (``float`` or ``numpy.ndarray``):
        Wavelengths to calculate the profile in unit of m.

    reference_wavelength (``float``):
        Central wavelength of the transition in unit of m.

    particle_mass (``float``):
        Mass of the particle corresponding to the transition in unit of kg.

    Returns
    -------
    absorption (``float`` or ``numpy.ndarray``):
        Absorption profile in function of ``wavelength_grid`` (it is either
        unitless if ``cell_density`` is a column density, or the unit is 1 / m
        if ``cell_density`` is a volumetric density).
    """
    w0 = reference_wavelength  # Reference wavelength in m
    wl_grid = wavelength_grid
    c_speed = 2.99792458e+08  # Speed of light in m / s
    k_b = 1.380649e-23  # Boltzmann's constant in J / K
    nu0 = c_speed / w0  # Reference frequency in Hz
    temp = cell_temperature
    mass = particle_mass

    # Calculate turbulence speed for the gas in m / s
    v_turb = (5 * k_b * temp / 3 / mass) ** 0.5
    # Calculate Doppler width
    u_th = (2 * k_b * temp / mass + v_turb ** 2) ** 0.5
    alpha_lambda = w0 / c_speed * u_th
    # alpha_lambda = (2 * k_b * temp / mass + v_turb ** 2) ** 0.5  # m
    # Calculate the Voigt profile
    # At the moment, calculating the Lorentzian width in wavelength space is
    # very hacky, it should be improved upon at some point
    gamma_nu = einstein_coeff / 4 / np.pi
    nuk = np.array([-gamma_nu / 2, gamma_nu / 2]) + nu0
    wk = c_speed / nuk
    gamma_lambda = np.diff(w0 - wk)[0]
    phi = voigt_profile(wl_grid - w0, alpha_lambda, gamma_lambda)

    # Finally calculate the cross-section sigma in m ** 2
    sigma = tools.cross_section(oscillator_strength, w0, alpha_lambda, phi)

    # The absorption is the density times the cross-section
    absorption = sigma * cell_density
    return absorption
