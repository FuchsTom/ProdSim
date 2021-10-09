.. _attr_values:

Attribute values
----------------

The following section lists all possible distributions and values that the user can give to a freely selectable
attribute. A list must always be passed whose syntax is the same. To uniquely select a distribution, the first element
of the list must be an identifier (string), which serves as a key for the distributions.The following elements in the
list represent parameters for the respective distribution. Thus, the length of the list depends on the selected
distribution and its number of free parameters.

* :ref:`Binary <binary>`
* :ref:`Normal <normal>`
* :ref:`Fix <fix>`
* :ref:`Uniform <uniform>`
* :ref:`Poisson <poisson>`
* :ref:`Exponential <exponential>`
* :ref:`Lognormal <lognormal>`

....

.. _binary:

Binary
******

To signal that an attribute should be binary distributed the identifier "b" must be used as the first argument in the
passed list. The second parameter specifies as a float the probability that the attribute takes the value 1.

.. code-block:: JSON

   "roasted": ["b",0.03]
   "cracked": ["b",0.012]

.. list-table:: Overview: binary
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "b"
     -
   * - Additional parameter
     - probability
     - Probability that the value will be 1
   * - Exceptions
     - InvalidFormat
     - List does not have length 2
   * -
     - InvalidType
     - Second parameter is not a float
   * -
     - InvalidValue
     - Second parameter is not between 0.0 and 1.0

....

.. _normal:

Normal
******

To signal that an attribute should be normal distributed the identifier "n" must be used as the first argument in the
passed list. The second parameter determines the mean value and the third the standard deviation. These additional
parameters can be integers or floats, where the standard deviation must be greater than or equal to zero.

.. code-block:: JSON

   "surface_quality": ["n",1,0.05]
   "weight": ["n",130.5,1]

.. list-table:: Overview: normal
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "n"
     -
   * - Additional parameter
     - mean
     - Type int oder float
   * -
     - standard deviation
     - Type int oder float
   * - Exceptions
     - InvalidFormat
     - List does not have length 3
   * -
     - InvalidType
     - Additional parameters are not float or int
   * -
     - InvalidValue
     - Standard deviation is less than 0

....

.. _fix:

Fix
***

To signal that an attribute should be a fix value the identifier "f" must be used as the first argument in the passed
list. The second parameter determines value the this attribute should have. Accepted types are integers and floats.

.. code-block:: JSON

   "prob_of_failure": ["f",0.01]
   "min_strength": ["f",920]

.. list-table:: Overview: fix
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "f"
     -
   * - Additional parameter
     - value
     - Type int oder float
   * - Exceptions
     - InvalidFormat
     - List does not have length 2
   * -
     - InvalidType
     - Value is not float or int

....

.. _uniform:

Uniform
*******

To signal that an attribute should be uniform distributed the identifier "u" must be used as the first argument in the
passed list. The second parameter determines the lower bound and the third the upper bound. These additional
parameters can be integers or floats, where the upper bound must be greater or equal to the lower bound. The specified
limits can also be realized by the random variable.

.. code-block:: JSON

   "N2_atmosphere": ["u",0.4,0.5]
   "weight": ["u",42.08,42.56]

.. list-table:: Overview: uniform
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "u"
     -
   * - Additional parameter
     - lower bound
     - Type int oder float
   * -
     - upper bound
     - Type int oder float
   * - Exceptions
     - InvalidFormat
     - List does not have length 3
   * -
     - InvalidType
     - Upper or lower bound is not float or int
   * -
     - InvalidValue
     - Upper bound is lower than lower bound

....

.. _poisson:

Poisson
*******

To signal that an attribute should be poisson distributed the identifier "p" must be used as the first argument in the
passed list. The second parameter determines the parameter lambda, which must be of type float or int and also greater
or equal to zero.

.. code-block:: JSON

   "num_cracks": ["p",1.8]
   "num_dents": ["p",4]

.. list-table:: Overview: poisson
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "p"
     -
   * - Additional parameter
     - parameter lambda
     - Type int oder float
   * - Exceptions
     - InvalidFormat
     - List does not have length 2
   * -
     - InvalidType
     - The parameter lambda is not float or int
   * -
     - InvalidValue
     - The parameter lambda is less than zero

....

.. _exponential:

Exponential
***********

To signal that an attribute should be exponential distributed the identifier "e" must be used as the first argument in
the passed list. The second parameter determines the parameter tau, which must be of type float or int and also greater
or equal to zero.

.. code-block:: JSON

   "carbon_content": ["e",0.1]
   "error_prob": ["e",0.02]

.. list-table:: Overview: exponential
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "e"
     -
   * - Additional parameter
     - parameter tau
     - Type int oder float
   * - Exceptions
     - InvalidFormat
     - List does not have length 2
   * -
     - InvalidType
     - The parameter tau is not float or int
   * -
     - InvalidValue
     - The parameter tau is less than zero

....

.. _lognormal:

Lognormal
*********

To signal that an attribute should be lognormal distributed the identifier "l" must be used as the first argument in
the passed list. The second parameter determines the mean and the third one sigma. Boat parameters must be of type float
or int, while the second one also must be greater or equal to zero.

.. code-block:: JSON

   "nitrogen_content": ["l",0.1,0.02]
   "surface_quality": ["l",10,0.4]

.. list-table:: Overview: lognormal
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "l"
     -
   * - Additional parameter
     - mean
     - Type int oder float
   * -
     - sigma
     - Type int oder float
   * - Exceptions
     - InvalidFormat
     - List does not have length 3
   * -
     - InvalidType
     - One of the parameters is not float or int
   * -
     - InvalidValue
     - The parameter sigma is less than zero

....

.. _chisquare:

Chisquare
*********

To signal that an attribute should be chisquare distributed the identifier "c" must be used as the first argument in
the passed list. The second parameter determines describes the degrees of freedom and must be of type float or int. The
degrees of freedom must be greater than (not equal to) zero.

.. code-block:: JSON

   "weight": ["c",4]
   "density": ["c",1.1]

.. list-table:: Overview: chisquare
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "c"
     -
   * - Additional parameter
     - degrees of freedom
     - Type int oder float
   * - Exceptions
     - InvalidFormat
     - List does not have length 2
   * -
     - InvalidType
     - Degrees of freedom is not float or int
   * -
     - InvalidValue
     - Degrees of freedom is less than or equal to zero

....

.. _standard-t:

Standard-t
**********

To signal that an attribute should be standard-t distributed the identifier "t" must be used as the first argument in
the passed list. The second parameter determines describes the degrees of freedom and must be of type float or int. The
degrees of freedom must be greater than (not equal to) zero.

.. code-block:: JSON

   "length_deviation": ["t",23.2]
   "weight_deviation": ["t",7]

.. list-table:: Overview: standard-t
   :header-rows: 1

   * - Aspect
     - Value
     - Explanation
   * - Identifier
     - "t"
     -
   * - Additional parameter
     - degrees of freedom
     - Type int oder float
   * - Exceptions
     - InvalidFormat
     - List does not have length 2
   * -
     - InvalidType
     - Degrees of freedom is not float or int
   * -
     - InvalidValue
     - Degrees of freedom is less than or equal to zero
