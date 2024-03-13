#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # read spectrum metadata only
    items = eds.Read("MassSpectrumItem", exclude=["Spectrum"], limit=20)
    
    # filter spectra
    spectrum_ids = []
    for item in items:
        if item.MSOrder == 2:
            spectrum_ids.append(item.IDs)
    
    # load full spectrum data
    items = eds.ReadMany("MassSpectrumItem", spectrum_ids)
    for item in items:
        print(item.Spectrum)
