#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import sys
import re
import pyeds
import pyeds.scripting

"""
This example shows some of the scripting node basics utilizing pyeds.scripting
tools.

It reads compounds and predicted compositions and creates a new top-level table
with unique formulas linked to corresponding compound(s). Additional columns is
also created in the Compounds table to directly show number of predicted
compositions. Using connection properties, once a unique formula is selected,
the linked Compounds sub-table directly shows the rank and SFit value for each
compound.

Although this example utilizes the tools even for exporting the data, it is not
required. Data can be formated and exported using any favourite data framework
instead. In such case, tab-separated values should be used for export. The full
expected export path of each table is accessible as table.DataFile. The main
response definition should be exported using response.ExportResponse().

To run this example just add the post-processing Scripting Node into your
workflow and provide some essential info. The "Path to Executable" should be set
directly to your Python executable (e.g. C:\Program Files\Python311\python.exe).
The "Command Line Arguments" should provide the absolute path to this script
followed by the %NODEARGS% (e.g. D:\Tmp\ex05-01_scripting_node.py %NODEARGS%).
"""

# init table names
TB_FORMULAS = "Unique Formulas"
TB_COMPOUNDS = "Compounds"
TB_COMPOSITIONS = "Predicted Compositions"
TB_FORMULAS_COMPOUNDS = "Formulas_Compounds"
TB_FORMULAS_COMPOSITIONS = "Formulas_Compositions"


def collect_formulas(result_path):
    """Collects unique predicted compositions."""
    
    # show message
    print("Loading compounds and formulas...")
    
    # init formula container as {formula: ({compounds IDs}, {compositions IDs}, mw, {atom: count}, {compound ID: (rank, sfit)})}
    formulas = {}
    
    # init counts container as [(compound ID, count),]
    counts = []
    
    # define simple formula pattern
    formula_pattern = re.compile("([A-Z][a-z]*)(\d*)?")
    
    # read data from result file using PyEDS
    with pyeds.EDS(result_path) as eds:
        
        # load all predicted compositions for all compounds
        compounds = eds.ReadHierarchy(
            path = [TB_COMPOUNDS, TB_COMPOSITIONS],
            properties = {TB_COMPOUNDS: []})
        
        # collect unique formulas
        for compound in compounds:
            
            # add count
            counts.append((compound.ID, len(compound.Children)))
            
            # process formulas
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
        
        return formulas, counts


def init_response(response_path):
    """Initializes all response tables."""
    
    # show message
    print("Initializing response...")
    
    # init node response
    response = pyeds.scripting.Response(response_path)
    
    # define formulas table
    formulas_t = response.AddTable(TB_FORMULAS)
    formulas_t.AddColumn("ID", pyeds.scripting.INT, pyeds.scripting.ID)
    formulas_t.AddColumn("Formula", pyeds.scripting.STRING)
    formulas_t.AddColumn("Molecular Weight", pyeds.scripting.FLOAT, FormatString="F5")
    formulas_t.AddColumn("# Compounds", pyeds.scripting.INT)
    formulas_t.AddColumn("# C", pyeds.scripting.INT)
    formulas_t.AddColumn("# H", pyeds.scripting.INT)
    formulas_t.AddColumn("# N", pyeds.scripting.INT)
    formulas_t.AddColumn("# O", pyeds.scripting.INT)
    formulas_t.AddColumn("# S", pyeds.scripting.INT)
    formulas_t.AddColumn("# P", pyeds.scripting.INT)
    formulas_t.AddColumn("# F", pyeds.scripting.INT)
    
    # define compounds update table
    compounds_t = response.AddTable(TB_COMPOUNDS)
    compounds_t.AddColumn("ID", pyeds.scripting.INT, pyeds.scripting.ID)
    compounds_t.AddColumn("# Compositions", pyeds.scripting.INT, PositionAfter="Formula")
    
    # define formula to compounds link table
    # make sure all ID columns starts with the table name followed by the ID column name
    # note that for now, only string can be used for connection columns
    formulas_compounds_t = response.AddConnection(TB_FORMULAS_COMPOUNDS, TB_FORMULAS, TB_COMPOUNDS)
    formulas_compounds_t.AddColumn(f"{TB_FORMULAS} ID", pyeds.scripting.INT, pyeds.scripting.ID)
    formulas_compounds_t.AddColumn(f"{TB_COMPOUNDS} ID", pyeds.scripting.INT, pyeds.scripting.ID)
    formulas_compounds_t.AddColumn("Formula Rank", pyeds.scripting.STRING)
    formulas_compounds_t.AddColumn("Formula SFit", pyeds.scripting.STRING, FormatString="F0")
    
    # define formula to compositions link table
    # make sure all ID columns starts with the table name followed by the ID column name
    formulas_compositions_t = response.AddConnection(TB_FORMULAS_COMPOSITIONS, TB_FORMULAS, TB_COMPOSITIONS)
    formulas_compositions_t.AddColumn(f"{TB_FORMULAS} ID", pyeds.scripting.INT, pyeds.scripting.ID)
    formulas_compositions_t.AddColumn(f"{TB_COMPOSITIONS} ID", pyeds.scripting.INT, pyeds.scripting.ID)
    formulas_compositions_t.AddColumn(f"{TB_COMPOSITIONS} WorkflowID", pyeds.scripting.INT, pyeds.scripting.WORKFLOW_ID)
    
    return response


def fill_tables(response, formulas, counts):
    """Fills response tables."""
    
    # show message
    print("Filling tables...")
    
    # get tables
    compounds_t = response.GetTable(TB_COMPOUNDS)
    formulas_t = response.GetTable(TB_FORMULAS)
    formulas_compounds_t = response.GetTable(TB_FORMULAS_COMPOUNDS)
    formulas_compositions_t = response.GetTable(TB_FORMULAS_COMPOSITIONS)
    
    # fill compounds table
    for compound_id, count in counts:
        compounds_t.AddRowData(compound_id, count)
    
    # fill formulas tables
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
        formulas_t.AddRowData(formula_id, formula, mw, len(compound_ids), C, H, N, O, S, P, F)
        
        # add to connection tables
        for compound_id in compound_ids:
            formulas_compounds_t.AddRowData(formula_id, compound_id, scores[compound_id][0], scores[compound_id][1])
        
        for composition_id in composition_ids:
            formulas_compositions_t.AddRowData(formula_id, composition_id[0], composition_id[1])


if __name__ == "__main__":
    
    # read node args
    node_args = pyeds.scripting.NodeArgs(sys.argv)
    
    # collect and process all compounds and predicted compositions
    unique_formulas, formulas_counts = collect_formulas(node_args.ResultFilePath)
    
    # initialize node response with all tables to be exported
    node_response = init_response(node_args.ExpectedResponsePath)
    
    # populate tables with data
    fill_tables(node_response, unique_formulas, formulas_counts)
    
    # export response definition and all tables data
    node_response.Export()
