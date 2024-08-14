# ArcGIS Pro Project Creator

This project is a terminal-based application built with the [Textual](https://textual.textualize.io/) Python library. It allows users to create new ArcGIS Pro projects by specifying project names, target folders, and optional datasets through a Text User Interface (TUI). The application is specifically designed to integrate with ArcGIS Pro environments.

## Features

- **Create ArcGIS Pro Projects:** Easily specify project names, target folders, and datasets.
- **Dynamic Dataset Addition:** Add multiple datasets to include in your project.
- **ArcGIS Pro Integration:** Uses the ArcGIS Pro Python environment to execute project creation scripts.
- **Terminal-Based Interface:** Leverages the Textual library for a smooth, terminal-based user experience.

## Installation

To run this project, ensure you have Python installed, along with the required dependencies.

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/arcgis-pro-project-creator.git
   cd arcgis-pro-project-creator
   ```

2. **Set up a virtual environment (optional but recommended):**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python good_start_textual.py
   ```

## Usage

Once the application is running:

1. Enter the project name.
2. Select the target folder where the project should be created.
3. Add any datasets you want to include in the project.
4. Click "Create Project" to generate the project.

The application will create the project in the specified location using the ArcGIS Pro Python environment.

## Requirements

- **Python** (3.8 or later recommended)
- **ArcGIS Pro Python environment** (specified in the script)

The dependencies listed in `requirements.txt` include:

- `textual`
- `rich`
- Other dependencies automatically installed with Textual

## Troubleshooting

### Common Issues

1. **Path Errors:** Ensure all file paths are correctly formatted, especially on Windows, where backslashes must be escaped (e.g., `c:\\path\\to\\folder`).

2. **ArcGIS Pro Integration:** Make sure the `arcgispro-py3` environment is properly configured and accessible.

### Logging

Any errors encountered during execution are logged in `error_log.txt` located in the project directory.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

If you have any questions or need further assistance, feel free to reach out.

**Author:** Daniel McVey
```

