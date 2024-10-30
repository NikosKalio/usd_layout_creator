"""
This module is designed to analyze USD (Universal Scene Description) files for testing purposes.
It extracts and processes USD attributes from 3D assets.

"""

from usd_utlis import get_usd_attributes
import csv
import os
from pxr import Usd, UsdGeom,Sdf, Gg

attributes = get_usd_attributes('assets/components/cabinet_with_hinged_doors_8.usda')

