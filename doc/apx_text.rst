APX Text
========

.. toctree::
   :maxdepth: 2
   :hidden:


.. highlight:: none

Data Signatures
---------------

Primitive types::

   a: string (null-terminated ASCII string)
   c: sint8  (signed 8-bit value)
   s: sint16 (signed 16-bit value)
   l: sint32 (signed 32-bit value)
   u: sint64 (signed 64-bit value)
   C: uint8  (unsigned 8-bit value)
   S: uint16 (unsigned 16-bit value)
   L: uint32 (unsigned 32-bit value)
   U: uint64 (unsigned 64-bit value)

Array type signature:
~~~~~~~~~~~~~~~~~~~~~

Each character may be optionally followed by the characters "[n]" where n is the array length (repeat count).
Strings (a) must always be defined as array types. Note that for strings the last character is always reserved for the null-terminator.

Examples::
   
   S[4]  array of uint16 with array-length=4
   a[20] string of 20 characters (the last character is reserved for the null terminator)

Complex type signature: 
~~~~~~~~~~~~~~~~~~~~~~~

Record types (struct-like elements) can be created by prepending your APX string with the '{' character and ending with '}'. Each record-element begins with a string
containing the name (embedded in '"' characters) followed by a primitive type character (with optional array modifier).
     
Examples::
   
   {"e1"C"e2"S"e3"a[5]}
     record with elements e1 (uint8), e2 (uint16) and e3 (string)

Port Signatures
---------------

.. image:: _static/APX_PortSignature.png


