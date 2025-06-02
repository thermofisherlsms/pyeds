#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import sys
import os.path
import re
import pyeds
import pyeds.scripting


# node settings
# Path to Executable: C:\Program Files\PythonXXX\python.exe
# Command Line Arguments: ABSOLUTE_PATH_TO_THIS_FILE %NODEARGS%

# define simple formula pattern
formula_pattern = re.compile("([A-Z][a-z]*)(\d*)?")

# read node args
nodeargs = pyeds.scripting.NodeArgs(sys.argv)

# init formula container as {formula: ({compounds IDs}, {compositions IDs}, mw, {atom: count}, {compound ID: (rank, sfit)})}
formulas = {}

# init table names
TB_FORMULAS = "Unique Formulas"
TB_COMPOUNDS = "Compounds"
TB_COMPOSITIONS = "Predicted Compositions"

# show message
print("Loading compounds and formulas...")

# read data from result file using PyEDS
with pyeds.EDS(nodeargs.ResultFilePath) as eds:
    
    # load all predicted compositions for all compounds
    compounds = eds.ReadHierarchy(
        path = [TB_COMPOUNDS, TB_COMPOSITIONS],
        properties = {TB_COMPOUNDS: []})
    
    # collect unique formulas
    for compound in compounds:
        for composition in compound.Children:
            
            # get previously stored formula
            formula = formulas.get(composition.Formula, None)
            
            # process new formula
            if not formula:
                
                # insert new formula
                formula = (set(), set(), composition.MolecularWeight, {}, {})
                formulas[composition.Formula] = formula
                
                # parse formula
                matches = formula_pattern.findall(composition.Formula)
                for element, count in matches:
                    count = int(count) if count else 1
                    formula[3][element] = count + formula[3].get(element, 0)
            
            # add IDs (note that for each table ALL IDs must be used)
            formula[0].add(compound.ID)  # compounds table has only single ID column
            formula[1].add((composition.ID, composition.WorkflowID))  # compositions table has two ID columns
            
            # add scores
            formula[4][compound.ID] = (composition.Rank, composition.SpectralFit)

# show message
print("Filling tables...")

# init data tables
formulas_table = []
formulas_compounds_table = []
formulas_compositions_table = []

# fill results tables
formula_id = 0
for formula in formulas:
    
    # increase formula ID
    formula_id += 1
    
    # get values
    compound_ids, composition_ids, mw, atoms, scores = formulas[formula]
    C = atoms.get('C', 0)
    H = atoms.get('H', 0)
    N = atoms.get('N', 0)
    O = atoms.get('O', 0)
    S = atoms.get('S', 0)
    P = atoms.get('P', 0)
    F = atoms.get('F', 0)
    
    # add to main table
    formulas_table.append(f"{formula_id}\t{formula}\t{mw}\t{C}\t{H}\t{N}\t{O}\t{S}\t{P}\t{F}")
    
    # add to connection tables
    for compound_id in compound_ids:
        formulas_compounds_table.append(f"{formula_id}\t{compound_id}\t{scores[compound_id][0]}\t{scores[compound_id][1]:.0f}")
    
    for composition_id in composition_ids:
        formulas_compositions_table.append(f"{formula_id}\t{composition_id[0]}\t{composition_id[1]}")

# show message
print("Creating response...")

# init node response
response = pyeds.scripting.Response(nodeargs.ExpectedResponsePath)

# define formulas table
path = os.path.join(response.WorkingDir, "formulas.txt")
formulas_t = response.AddTable(TB_FORMULAS, path)
formulas_t.AddColumn("ID", pyeds.scripting.INT, pyeds.scripting.ID)
formulas_t.AddColumn("Formula", pyeds.scripting.STRING)
formulas_t.AddColumn("Molecular Weight", pyeds.scripting.FLOAT)
formulas_t.AddColumn("# C", pyeds.scripting.INT)
formulas_t.AddColumn("# H", pyeds.scripting.INT)
formulas_t.AddColumn("# N", pyeds.scripting.INT)
formulas_t.AddColumn("# O", pyeds.scripting.INT)
formulas_t.AddColumn("# S", pyeds.scripting.INT)
formulas_t.AddColumn("# P", pyeds.scripting.INT)
formulas_t.AddColumn("# F", pyeds.scripting.INT)

# define formula to compounds link table
# make sure all ID columns starts with the table name followed by the ID column name
# note that currently only the strings are supported for custom connection properties
path = os.path.join(response.WorkingDir, "formulas_compounds.txt")
formulas_compounds_t = response.AddConnection("Formulas_Compounds", path, TB_FORMULAS, TB_COMPOUNDS)
formulas_compounds_t.AddColumn(f"{TB_FORMULAS} ID", pyeds.scripting.INT, pyeds.scripting.ID)
formulas_compounds_t.AddColumn(f"{TB_COMPOUNDS} ID", pyeds.scripting.INT, pyeds.scripting.ID)
formulas_compounds_t.AddColumn("Formula Rank", pyeds.scripting.STRING)
formulas_compounds_t.AddColumn("Formula SFit", pyeds.scripting.STRING)

# define formula to compositions link table
# make sure all ID columns starts with the table name followed by the ID column name
path = os.path.join(response.WorkingDir, "formulas_compositions.txt")
formulas_compositions_t = response.AddConnection("Formulas_Compositions", path, TB_FORMULAS, TB_COMPOSITIONS)
formulas_compositions_t.AddColumn(f"{TB_FORMULAS} ID", pyeds.scripting.INT, pyeds.scripting.ID)
formulas_compositions_t.AddColumn(f"{TB_COMPOSITIONS} ID", pyeds.scripting.INT, pyeds.scripting.ID)
formulas_compositions_t.AddColumn(f"{TB_COMPOSITIONS} WorkflowID", pyeds.scripting.INT, pyeds.scripting.WORKFLOW_ID)

# show message
print("Exporting data...")

# export response definition
response.Save()

# export tables
with open(formulas_t.DataFile, 'w', encoding='utf-8') as wf:
    wf.write(formulas_t.Header+"\n")
    wf.write("\n".join(formulas_table))

with open(formulas_compounds_t.DataFile, 'w', encoding='utf-8') as wf:
    wf.write(formulas_compounds_t.Header+"\n")
    wf.write("\n".join(formulas_compounds_table))

with open(formulas_compositions_t.DataFile, 'w', encoding='utf-8') as wf:
    wf.write(formulas_compositions_t.Header+"\n")
    wf.write("\n".join(formulas_compositions_table))
