# PyQt Stackbrowser (currently in develpment)

Newest stack browser version built using PyQt4. Allows browsing of multi-page TIFF hyperstack data, and currently supports visual overlays in two formats:
* __Vascular Mode:__ Collections of nodes, edges, and slabs (i.e. Nodes and edges from graphs, with slabs as points along edges serving as morphology descriptors)
* __Spine Mode:__ Collections of points and lines (where points and lines are unrelated)

To run the stack browser, ensure all files in the "PyQt Stackbrowser" folder are in your working directory, then run __stackbrowserQt.py__.

Using a pre-packaged Python distribution such as Anaconda is strongly recommended.



## Dependencies

* **__Python 2.7__**
* numpy
* pandas
* [tifffile](https://pypi.python.org/pypi/tifffile)
* [PyQt4](https://www.riverbankcomputing.com/software/pyqt/download)
* [python-igraph](http://igraph.org/python/)


## Running the stack browser

At startup, you will need to choose a hyperstack to open. Depending on your desired data mode, please have a directory prepared in one of the following formats:

### Vascular Mode

* __nodes/__
  - Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_nT.txt
  - ...
* __edges/__
  - Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_eT.txt
  - ...
* __slabs/__
  - Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_sD.txt
  - ...
* Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_ch1.tif
* Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_ch2.tif
* ...

### Spine Mode

* __stackdb/__
  - SESSIONNAME_sSESSIONNUMBER_db2.txt
  - ...
* __line/__
  - SESSIONNAME_sSESSIONNUMBER_l.txt
  - ...
* __raw/__
  - SESSIONNAME_sSESSIONNUMBER_ch1.tif
  - SESSIONNAME_sSESSIONNUMBER_ch2.tif
  - ...

Then, select the stack to open (start with channel 1).

### Controls

Action | Key
--- | ---
__Pan__ | Up, down, left, right
__Center__ | Enter
__Zoom__ | +, -
__Scroll__ | Mouse wheel
__View channel [1, 2]__ | 1, 2
__Next/previous time point__ | Shift + left, right


For more info, see source documentation.
