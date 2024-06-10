import subprocess, os
# Set up the necessary environment variables
env = os.environ.copy()
view = 'CDS_TRN_V_CKT_GG_OH_UG_CONCAT'
# CDS_ALL_COND_DM
view = 'CDS_ALL_STRUC_DM'

# Paths and arguments
qgis_script_path = r'C:\Users\mcveydb\dev\GIS-Utilities\arcgis pro\qgis\qgis_savefeatures.py'
# qgis_script_path = r'C:\Users\mcveydb\dev\GIS-Utilities\arcgis pro\qgis\ALL_VIEWS.py'
# qgis_script_path = r"C:\Users\mcveydb\dev\GIS-Utilities\arcgis pro\qgis\simple_test.py"
# qgis_python_path = r'C:\Program Files\QGIS 3.34.4\apps\qgis-ltr\python'
input_path = f"""oracle://dbname='p701DG_CGIS' host=ayxap07-scan.sce.com port=1526 authcfg=ikykuzu key='M3D_FID' estimatedmetadata=true srid=1026911 type=Point table="TCGMDMART"."{view}" (M3D_GEOGRAPHIC_LOCATION)"""
output_path = fr'C:/data/datamart/{view}_from_propython.gdb'

# Construct the command with arguments
cmd = ['C:\OSGeo4W\OSGeo4W.bat','python-qgis-ltr', qgis_script_path, '--input', input_path, '--output', output_path]
# cmd = ['C:\OSGeo4W\OSGeo4W.bat','python-qgis-ltr', qgis_script_path]
# cmd = 'cmd /c "C:\\OSGeo4W\\OSGeo4W.bat python-qgis-ltr \\"C:\\Users\\mcveydb\\dev\\GIS-Utilities\\arcgis pro\\qgis\\qgis_savefeatures.py\\" --input \\"oracle://dbname=\'p701DG_CGIS\' host=ayxap07-scan.sce.com port=1526 authcfg=ikykuzu key=\'M3D_FID\' estimatedmetadata=true srid=1026911 type=Point table=\\\\"TCGMDMART\\\\.\\\\"CDS_TRN_V_CKT_GG_OH_UG_CONCAT\\\\" (M3D_GEOGRAPHIC_LOCATION)\\" --output \\"C:/data/datamart/CDS_TRN_V_CKT_GG_OH_UG_CONCAT_from_propython.gdb\\""'

# Print the command to verify it
print(cmd)

# Execute the command
subprocess.run(cmd, shell=True, env=env)

# Verify each part of the cmd
# for item in cmd:
#     print(item, type(item))
# Execute the command
# subprocess.run(cmd,shell=True)


# command = '"C:\\OSGeo4W\\OSGeo4W.bat" python-qgis-ltr "C:\\Users\\mcveydb\\dev\\GIS-Utilities\\arcgis pro\\qgis\\simple_test.py" --input "oracle://dbname=\'p701DG_CGIS\' host=ayxap07-scan.sce.com port=1526 authcfg=ikykuzu key=\'M3D_FID\' estimatedmetadata=true srid=1026911 type=Point table=\\"TCGMDMART\\".\\"CDS_ALL_STRUC_DM\\" (M3D_GEOGRAPHIC_LOCATION)" --output C:/data/datamart/CDS_ALL_STRUC_DM_from_propython.gdb'

# result = subprocess.run(command, shell=True, env=env, text=True, capture_output=True)
# print(result.stdout)
