.. _api:

API Reference
=============

``Environment``
---------------

The Environment class represents the central element of the library. All offered simulation functionalities are
available to the user in the methods through an object of this class. In addition, the environment controls all
program-internal method calls as well as access to the process data in the background.

.. automodule:: environment
   :members:

``Estimator``
---------------

The Estimator class offers some functionalities through which the runtime behavior of the simulation can be estimated.
Alternatively, a reference simulation with a short simulation time can be performed, and the measured simulation time
can be scaled proportionally. However, the function est_function is especially useful for developing suitable process
functions.

.. automodule:: estimator
   :members:
