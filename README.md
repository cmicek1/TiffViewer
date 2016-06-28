# TiffViewer

Browser for multi-page TIFF hyperstack data, and utilities for accessing per-time point databases of nodes, edges, and slabs (points-of-interest along edges).

To run the stack browser, ensure all files in the repository are in your working directory, then run __stackbrowser.py__. The database utilities (__nodedb.py__, __edgedb.py__, and __slabdb.py__) will function both in tandem with the stack browser, as well as alone when passed a pandas DataFrame.

Using a pre-packaged Python distribution such as Anaconda is strongly recommended.



## Dependencies

* **__Python 2.7__**
* [tifffile] (https://pypi.python.org/pypi/tifffile)
* [pygame] (http://www.pygame.org/wiki/GettingStarted)
* numpy
* pandas


## Running the stack browser

At startup, you will need to choose a hyperstack to open. Please have a directory prepared in the following format:

* __nodes/__
- Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_nT.txt
- ...
* __edges/__
- Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_eT.txt
- ...
* __slabs/__
- Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_sT.txt
- ...
* Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_ch1.tif
* Xyyyymmdd_aANUMALNUMBER_STACKNUMBER_ch2.tif
* ...

Then, select the stack to open (start w/ channel 1).

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
