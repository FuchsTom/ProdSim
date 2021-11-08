# ProdSim - Changelog

***

All notable changes to this project will be documented in this file. 

### 0.0.2 (2021-11-08)
***

**New Method**

* ``data_to_hdf5`` was added to the simulation environment. Provides export of simulation data in binary hierarchical 
  format hdf5. 

### 0.0.1 (2021-09-27)
***

**Bug Fix**

* If main workpieces are tracked via ``track_components`` (parameter of ``simulate``), but not their sub workpieces, 
  this has led to a ``KeyError`` in the ``track_nested_item`` (tracker.py) method . This issue was fixed by modifying 
  the ``track_nested_item`` method. 

### 0.0.0 (2021-09-13)
*** 

**Initial Release**