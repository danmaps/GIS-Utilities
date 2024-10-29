import saspy

# Connect to SAS using the default configuration
sas = saspy.SASsession(cfgname='winiomwin')

# Run a SAS procedure, just to prove I'm connected
sas_code = """
proc print data=sashelp.class;
run;
"""
sas.submit(sas_code)