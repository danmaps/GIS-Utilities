import sys, argparse,os
from qgis.core import QgsApplication
from qgis.analysis import QgsNativeAlgorithms
# Save the original PYTHONHOME for later restoration
original_pythonhome = os.environ.get('PYTHONHOME', '')

# Temporarily set PYTHONHOME to the QGIS Python path
qgis_python_path = r"C:\Program Files\QGIS 3.34.4\apps\qgis-ltr\python"
os.environ['PYTHONHOME'] = qgis_python_path


# Setup argparse to accept input and output parameters
parser = argparse.ArgumentParser(description='Run QGIS Process')
parser.add_argument('--input', type=str, help='Input layer')
parser.add_argument('--output', type=str, help='Output layer')
args = parser.parse_args()

# Initialize QGIS Application
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.34.4", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Register QGIS native algorithms
sys.path.append(r'C:\Program Files\QGIS 3.34.4\apps\qgis-ltr\plugins')
from qgis import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

# Run processing using arguments
processing.run("native:savefeatures", {
    'INPUT': args.input,
    'OUTPUT': args.output,
    'LAYER_NAME':'',
    'DATASOURCE_OPTIONS':'',
    'LAYER_OPTIONS':'',
    'ACTION_ON_EXISTING_FILE':0
    }
)

qgs.exitQgis()

# Restore the original PYTHONHOME
os.environ['PYTHONHOME'] = original_pythonhome