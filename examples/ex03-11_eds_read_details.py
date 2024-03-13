#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# For latest PD version, some data like spectra and traces are stored in external
# file. This fine can be accessed the same way as a regular result.

# define result file
report_file = "__USE_YOU_OWN_PD_FILE__.pdResult"

# define details file
details_file = "__USE_YOU_OWN_PD_FILE__.pdResultDetails"

# open files using the 'with' statement
with (pyeds.EDS(report_file) as report,
      pyeds.EDS(details_file) as details):
    
    # read PSMs and connected spectrum i nfo
    for psm in report.ReadHierarchy(["PSMs", "MSnSpectrumInfo"], limits=5):
        print(psm.MassOverCharge, psm.Sequence, psm.XCorr)
        
        # get spectra IDs
        ids = [s.IDs for s in psm.Children]
        
        # read spectra from details
        for spectrum in details.ReadMany("MassSpectrumItem", ids):
            print(spectrum.Spectrum)
