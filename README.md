# Data service

## Description 

This module is responsible for reports management. Exposed APi provides ability to:

* create report
* get report details by id
* get reports list
* get collected data from certain sensor with given label

Api specification is present in `api-store` project under `data` prefix.

## Configuration

This module contains several data sources classes, one per one sensor type. 

### Data sources configuration

#### Sensor types
* data.dataSources.{sensor-mean}.sensorType
* Sensor type name

#### Available labels
* data.dataSources.{sensor-mean}.availableLabels
* List of available sensor mean labels

#### Available {sensor-mean} values:
* temperatureMean
* pressureMean
* flowRateMean
* gasCompositionMean
* compressorState

