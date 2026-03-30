# clyde-space-recruitment
A project for the geospatial data engineer recruitment task

This directory holds the requirements, data, scripts required to generate a geojson file that contains information about volcanic eruptions that have occurred since 1700 across the world.

## Data

The raw data files were downloaded from https://volcano.si.edu/, a database compiled and managed by Global Volcanism Program, Smithsonian Institution. Two datasets are used, the first is a list of eruptions in from the holocene period, the second contains more information about individual volcanos.

## Code

There is only one script written in Python. It will import the datasets mentioned above and process them generating a geojson file conatining eruption information dating back to 1700 and a short data quality report.

To run the script call "python volcanic_eruptions.py" from within the src directory or use the appropriate path for your machine.

## Outputs

Outputs will be saved to the outputs folder along with the quality report. These will be overwritten each time the script is run.

## Requirements

A requirements.txt file lists the environment requirements to successfully run the script. It was created using conda and therefore conda should be used to create the environment using this file.

## Web Map

The eruptions_cleaned.geojson file has been published as a Hosted Feature Layer on ArcGIS online here: https://www.arcgis.com/home/item.html?id=177e98133e594be4a4762db0666dd8bb

A web map of the data is available at: https://www.arcgis.com/apps/mapviewer/index.html?webmap=9eadfd76c897423fa03353607bf6c9ca&center=-102.559076%2C10.445166&scale=18489297.737236