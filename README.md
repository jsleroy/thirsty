[![GitHub stars](https://img.shields.io/github/stars/jsleroy/thirsty.svg?style=social)](https://github.com/jsleroy/thirsty/stargazers)

<p align="center">
<img src="docs/assets/logo.png" alt="Thirsty Logo" width="200"/>
</p>

# Thirsty

Add hydration points to your GPX tracks automatically 🚴‍♂️💧

<p align="center">
<a href="https://www.paypal.com/donate/?business=TJAXC3T4WD66L&no_recurring=0&currency_code=EUR" target="_blank">
<img src="https://img.shields.io/badge/Donate-PayPal-blue.svg?style=for-the-badge" alt="Donate with PayPal"/>
</a>
</p>

Thirsty is a Python tool that enhances your GPX files by adding Points of Interest (POIs), particularly drinking water points, to your cycling or running routes. It integrates with the Overpass API to query OpenStreetMap for relevant points along your route and adds them to the GPX file. Ideal for long-distance cycling events, ultra races, or any activity where hydration points matter!

Found a bug? Need a new feature? [Open an Issue](https://github.com/jsleroy/thirsty/issues)!

## 📷 Screenshots

### Add Water Points to Your GPX

<p align="center">
<img src="docs/assets/before-after.png" alt="Before" width="80%"/>
</p>

### Visualize on a Map

<p align="center">
<img src="docs/assets/map.png" alt="Map Display" width="80%"/>
</p>

### Simple Command-Line Interface

<p align="center">
<img src="docs/assets/terminal.png" alt="Terminal Usage" width="80%"/>
</p>

## Features

- **Query Overpass API**: Fetch drinking water POIs from OpenStreetMap.
- **Bounding Box Filtering**: Filter POIs around a defined area to match your GPX route.
- **Distance-based Filtering**: Ensures POIs are within a defined proximity of your GPX track.
- **Supports GPX from URL and Local Files**: Easily work with GPX files from your device or download them from a URL.
- **In-Memory Handling**: No need for temporary files; everything is handled in memory for speed.
- **Progress Bar**: Monitor download and processing progress with the `rich` module.

## POI Type Selection

By default, **Thirsty** searches for public drinking water fountains (`drinking_water` POIs).
You can customize which types of potable water points you want to add using the `--poi-type` (or `-p`) option.

- You can specify **one or more** POI types by repeating the `-p` option.
- If no `-p` option is specified, `drinking_water` will be used automatically.

### Available POI types

| POI Type          | Description                                                              |
| :---------------- | :----------------------------------------------------------------------- |
| `drinking_water`  | Public drinking water fountains (default).                               |
| `water_point`     | Water refill stations for caravans, RVs, or marinas (only potable ones). |
| `water_tap`       | Taps providing potable water.                                            |
| `spring`          | Natural springs with potable water.                                      |
| `fountain`        | Public decorative fountains explicitly marked as potable.                |
| `watering_places` | Watering places indented for animals explicitly marked as potable.       |
| `non-potable`     | All water sources that are not explicitly marked as potable.             |

### Example usage

Use default drinking water points:

```bash
thirsty -i trace.gpx -o trace_with_poi.gpx
```

Use **only** springs and water taps:

```bash
thirsty -i trace.gpx -o trace_with_poi.gpx -p spring -p tap
```
If an invalid POI type is provided, the program will display an error message and exit.

## ⚙️ Installation

Clone this repository and set up a virtual environment:

```bash
git clone https://github.com/jsleroy/thirsty
cd thirsty
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install .
```

## Usage

### Download GPX from URL and Add POIs

This example shows how to download a GPX file from a URL, add drinking water POIs to the route, and save the modified GPX to an output file.

```bash
thirsty https://example.com/yourfile.gpx output.gpx --distance 150
```

- **URL or Local GPX**: Supports both local files and downloading from a URL.
- **Distance**: Optionally specify the maximum distance (in meters) from the track for POIs (default: 100 meters).

### Local GPX File Usage

You can also process a local GPX file:

```bash
thirsty input.gpx output.gpx --distance 150
```

### Features in Detail

#### 1. Bounding Box Filtering
- Queries the Overpass API for drinking water POIs within the bounding box of the GPX file's route.

#### 2. Distance-based Filtering
- Filters POIs that are within a specified distance from the GPX track. This ensures that only nearby POIs are added to the GPX file.

#### 3. In-Memory File Handling
- Both downloaded and local GPX files are handled entirely in memory, eliminating the need for temporary files and speeding up the process.

#### 4. Progress Bar
- During the download process, the script shows a progress bar (using the `rich` library) so you can track the download status in real-time.

## ️ Development

### Requirements

- Python 3.7+
- `requests`: For HTTP requests to Overpass API and downloading GPX files.
- `gpxpy`: For reading and writing GPX files.
- `rich`: For the progress bar and rich text output.

### Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Running the CLI

You can run the script directly from the command line. Make sure to provide the appropriate input parameters (either a local file or a URL) and specify the output file:

```bash
thirsty input.gpx output.gpx --distance 150
```

## Contributing

1. Fork this repository and create a new branch.
2. Make your changes and commit them.
3. Push your changes to your fork.
4. Create a Pull Request with a detailed description of your changes.

## License

This project is licensed under the [GNU GPL v3 License](LICENSE).
