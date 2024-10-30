"""
This module defines the data models for a USD-based furniture assembly system, specifically focused on workbench configurations.
It uses Pydantic models to validate and manage:
- Cabinet components and assemblies
- Workbench tops
- Panel configurations (in matrix/row arrangements)
- Other auxiliary assets

The models include validation logic to ensure dimensional consistency between components and provide utilities
for calculating total lengths and checking component compatibility. An assembly model should define a caninet assembly.

These models are the "heart" of any pipeline that uses LISTA files to create assemblies. e.g. We can transform this model to 3D-Future style datatypes, or conver to USD.
"""

from pydantic import BaseModel, Field, computed_field, model_validator
from typing import List, Optional, Tuple
from dataclasses import dataclass


class CabinetModel(BaseModel):
    name: str
    asset_path: str = Field(..., description="Path to the USD file for this cabinet")
    dimensions: Tuple[float, float, float] = Field(..., description="Dimensions (x, y, z) from xformOp:scale")
    function: str = Field(..., description="Function of the cabinet")
    type: str = Field(..., description="Type of the cabinet")
    color: Tuple[float, float, float] = Field(..., description="Color of the cabinet as RGB values")
    material: str = Field(..., description="Material of the cabinet")


class PanelModel(BaseModel):
    length: int = Field(..., description="Length of the panel in millimeters")
    asset_path: str = Field(..., description="Path to the USD file for this panel")


class WorkbenchTopModel(BaseModel):
    name: str
    asset_path: str = Field(..., description="Path to the USD file for this workbench top")
    dimensions: Tuple[float, float, float] = Field(..., description="Dimensions (x, y, z) from xformOp:scale")
    function: str = Field(..., description="Function of the workbench top")
    type: str = Field(..., description="Type of the workbench top")
    color: Tuple[float, float, float] = Field(..., description="Color of the workbench top as RGB values")
    material: str = Field(..., description="Material of the workbench top")


class PanelRowModel(BaseModel):
    row_name: str = Field(..., description="Name or identifier of the panel row")
    panels: List[PanelModel] = Field(..., description="List of panels in this row")

    @property
    def total_row_length(self):
        """Returns the sum of the lengths of all panels in the row."""
        return sum(panel.length for panel in self.panels)


class PanelMatrixModel(BaseModel):
    rows: List[PanelRowModel] = Field(..., description="List of panel rows forming a matrix")

    @property
    def total_matrix_length(self):
        """Returns the total length defined by the sum of lengths of the longest row."""
        if not self.rows:
            return 0
        return max(row.total_row_length for row in self.rows)


class OtherAssetModel(BaseModel):
    name: str
    height: int = Field(..., description="Height of the asset in millimeters")
    length: int = Field(..., description="Length of the asset in millimeters")
    depth: int = Field(..., description="Depth of the asset in millimeters")
    width: int = Field(..., description="Width of the asset in millimeters")
    asset_path: str = Field(..., description="Path to the USD file for this asset")
    position: str = Field(..., description="Position of the asset relative to the assembly, e.g., 'side', 'corner', 'back'")


class CabinetAssembly(BaseModel):
    cabinets: List[CabinetModel] = Field(..., description="List of cabinets included in the assembly")

    @computed_field
    @property
    def total_length(self) -> float:
        """Calculate the total width of all cabinets in the assembly."""
        return sum(cabinet.dimensions[0] for cabinet in self.cabinets)

    def check_consistency(self) -> List[str]:
        warnings = []
        if not self.cabinets:
            return warnings

        first_cabinet = self.cabinets[0]
        reference_height = first_cabinet.dimensions[1]  # Assuming y is height
        reference_depth = first_cabinet.dimensions[2]  # Assuming z is depth

        for i, cabinet in enumerate(self.cabinets[1:], start=1):
            if cabinet.dimensions[1] != reference_height:
                warnings.append(f"Warning: Cabinet {i} has a different height ({cabinet.dimensions[1]}) than the first cabinet ({reference_height})")
            if cabinet.dimensions[2] != reference_depth:
                warnings.append(f"Warning: Cabinet {i} has a different depth ({cabinet.dimensions[2]}) than the first cabinet ({reference_depth})")

        return warnings


class AssemblyModel(BaseModel):
    cabinets: CabinetAssembly
    workbench_top: WorkbenchTopModel
    other_assets: Optional[List[OtherAssetModel]] = Field(None, description="Optional additional assets like heavy-duty storage or other furniture")

    @computed_field
    @property
    def total_length(self) -> float:
        """Calculate the total length of the assembly."""
        return self.cabinets.total_length

    def adjust_workbench_top(self) -> None:
        """Adjust the workbench top to match the cabinet assembly length."""
        cabinet_length = self.cabinets.total_length
        workbench_length = self.workbench_top.dimensions[0]
        
        if abs(cabinet_length - workbench_length) > 0.001:  # Check if difference is greater than 1mm
            new_dimensions = (cabinet_length, self.workbench_top.dimensions[1], self.workbench_top.dimensions[2])
            self.workbench_top = WorkbenchTopModel(
                name=self.workbench_top.name,
                asset_path=self.workbench_top.asset_path,
                dimensions=new_dimensions,
                function=self.workbench_top.function,
                type=self.workbench_top.type,
                color=self.workbench_top.color,
                material=self.workbench_top.material
            )

    def check_consistency(self) -> List[str]:
        warnings = []
        
        # Check and adjust workbench top length
        cabinet_length_mm = round(self.cabinets.total_length * 1000)
        workbench_length_mm = round(self.workbench_top.dimensions[0] * 1000)
        
        if cabinet_length_mm != workbench_length_mm:
            warnings.append(f"Warning: Workbench top length ({workbench_length_mm} mm) does not match cabinet assembly length ({cabinet_length_mm} mm). Adjusting workbench top.")
            self.adjust_workbench_top()

        # Add cabinet consistency checks
        warnings.extend(self.cabinets.check_consistency())

        return warnings

    @model_validator(mode='after')
    def validate_and_adjust_assembly(self) -> 'AssemblyModel':
        self.adjust_workbench_top()
        return self
