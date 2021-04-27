# PyEDS

The *PyEDS* is a Python library providing collection of utilities to conveniently access and display results from Thermo
Discoverer software like *Compound Discoverer* or *Proteome Discoverer*. Although the data are stored in open format
already (SQLite database), reading complex hierarchies is still not a trivial task and requires certain knowledge of
internal mechanisms. Using *PyEDS*, all the hard work is done automatically, so you can focus more on your research
instead of how to read the data.

The *PyEDS* library provides several tools to read data (*pyeds.EDS*), displaying tables metadata (*pyeds.Summary*) as
well as displaying actual data in nicely formatted tables (*pyeds.Review*).

Please see the [examples](https://github.com/thermofisherlsms/pyeds/tree/master/examples) folder to learn more about
available tools and functions.

### Show File Info

```python
import pyeds

# open result file using 'with' statement
with pyeds.Summary("examples/data.cdResult") as summary:
    
    # show full info
    summary.ShowAll()
```

### Reading Individual Tables

```python
import pyeds

# open result file using 'with' statement
with pyeds.EDS("examples/data.cdResult") as eds:
    
    # read top 10 most abundant compounds in specific RT range
    items_iter = eds.Read("Compounds",
        query = "RetentionTime > 3.8 AND RetentionTime < 4.1 AND Name != ''",
        order = "MaxArea",
        desc = True,
        limit = 10)
    
    # print some properties
    for item in items_iter:
        print(item.Name, item.Formula, item.RetentionTime)
```

### Reading Hierarchies

```python
import pyeds

# open result file using 'with' statement
with pyeds.EDS("examples/data.cdResult") as eds:
    
    # define connection path and items to keep
    path = ["Compounds", "BestHitIonInstanceItem", "MassSpectrumItem"]
    keep = ["Compounds", "MassSpectrumItem"]
    
    # limit spectra to MS2 only
    queries = {
        "BestHitIonInstanceItem": "BestHitType = 2",
        "MassSpectrumItem": "MSOrder = 2"}
    
    # read 2 most abundant items only
    orders = {"Compounds": "MaxArea"}
    descs = {"Compounds": True}
    limits = {"Compounds": 2}
    
    # read data
    items_iter = eds.ReadHierarchy(
        path,
        keep = keep,
        queries = queries,
        orders = orders,
        descs = descs,
        limits = limits)
    
    # print some properties
    for item in items_iter:
        
        # print compound properties
        print(item.Name, item.Formula, item.RetentionTime)
        
        # print mass spectra
        for child in item.Children:
            print("\t", child.Spectrum)
```

### Display Tables

```python
import pyeds

# init tools
eds = pyeds.EDS("examples/data.cdResult")
review = pyeds.Review()

# open result file and review using the 'with' statement
with eds, review:
    
    # read data
    path = ["Compounds", "Compounds per File"]
    items = eds.ReadHierarchy(path,
        limits = {"Compounds": 3},
        orders = {"Compounds": "MaxArea"},
        descs = {"Compounds": True})
    
    # display full hierarchy
    review.InsertItems(items, hierarchy=True, header=True)

# show review
review.Show()
```

## Requirements

- [Python 3.6+](https://www.python.org)
- [Numpy](https://pypi.org/project/numpy/)
- [[RDKit]](https://www.rdkit.org/) (Optional, used to display MOL structures.)
- [[Matplotlib]](https://pypi.org/project/matplotlib/) (Optional, used to display spectra and traces.)


## Installation

The *PyEDS* library is fully implemented in Python. No additional compiler is necessary. After downloading the source
code just run the following command from the folder containing the *setup.py*. Unfortunately there is already a package
with the same name on *pypi.org* therefore we cannot distribute it there.


```$ python setup.py install```

or

```$ pip install .```

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

For Research Use Only. Not for use in diagnostic procedures.