# Blender Decimate Ground Addon

## Overview
This Blender addon optimizes ground meshes by decimating only the ground portion of a high-poly object. It simplifies the mesh to improve performance while maintaining the object's visual integrity.

## Features
- **Ground Mesh Creation**: Generates a subdivided square mesh that covers the X and Y span of the high-poly object.
- **Vertex Adjustment**: Moves the vertices of each square up until they are just below any face of the high-poly object.
- **Selective Decimation**: Deletes faces of the high-poly object that are within a specified depth from the ground mesh squares, preserving the non-ground parts of the object.

## Usage
1. Select the high-poly object you wish to decimate.
2. Specify the depth for selective decimation.
3. Run the addon to create the ground mesh and perform the decimation.

For detailed instructions and more information, please refer to the Documentation.

## Installation
To install the addon:
1. Download the `.zip` file from the GitHub repository.
2. In Blender, go to `Edit > Preferences > Add-ons`.
3. Click `Install` and select the downloaded `.zip` file.
4. Enable the addon from the list.

## Contributing
Contributions to the Blender Decimate Ground Addon are welcome. Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
