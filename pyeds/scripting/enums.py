#  Created by Martin Strohalm, Thermo Fisher Scientific

# define enums
CSV = 'CSV'
CSV_CONN = 'CSVConnectionTable'
DATA_FORMAT = (CSV, CSV_CONN)

ID = 'ID'
WORKFLOW_ID = 'WorkflowID'
OTHER = 'Other'
ID_FLAG = (ID, WORKFLOW_ID, OTHER)

STRING = 'String'
INT = 'Int'
LONG = 'Long'
FLOAT = 'Float'
BOOLEAN = 'Boolean'
DATA_TYPE = (STRING, INT, LONG, FLOAT, BOOLEAN)

NUMERIC = 'Numeric'
CATEGORICAL = 'Categorical'
ORDINAL = 'Ordinal'
PLOT_TYPE = (NUMERIC, CATEGORICAL, ORDINAL)
