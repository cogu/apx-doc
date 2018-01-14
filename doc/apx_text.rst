APX Text
========

.. toctree::
   :maxdepth: 2
   :hidden:

.. highlight:: none

APX Text is a human-readable data definition language used to describe signals sent/received in an automotive system. APX files are stored on disk using the .apx file ending.

Example (Example.apx)::

   APX/1.2
   N"Example"
   T"VehicleSpeed_T"S
   T"EngineSpeed_T"S
   P"VehicleSpeed"T[0]:=65535
   P"EngineSpeed"T[1]:=65535

Components
----------

Software components are blocks which encapsulates a related set of function or data (high cohesion).
In the automotive industry they typically communicate with each other using signals.
If a component is sending a signal it is said to be a *provider* of the signal. On component level this is indicated by provide (or output) ports.
If a component is receiving a signal it is said to be a *requester* of the signal. On component level this is indicated by require (or input) ports.

Example Sender-Receiver
~~~~~~~~~~~~~~~~~~~~~~~

The Sender component (which has the name "Sender") provides the following signals:

+--------------+-----------+---------------+
|   Name       | Data Type | Initial Value |
+==============+===========+===============+
| VehicleSpeed |   uint16  |     65535     |
+--------------+-----------+---------------+
| EngineSpeed  |   uint16  |     65535     |
+--------------+-----------+---------------+

The Receiver component (which has the name "Receiver") requires the following signals:

+--------------+-----------+---------------+
|   Name       | Data Type | Initial Value |
+==============+===========+===============+
| VehicleSpeed |   uint16  |     65535     |
+--------------+-----------+---------------+
| EngineSpeed  |   uint16  |     65535     |
+--------------+-----------+---------------+

.. image:: _static/APX_SenderReceiver.png

The Sender component has two provide ports and can be represented in APX Text as follows::

   APX/1.2
   N"Sender"
   P"VehicleSpeed"S:=65535
   P"EngineSpeed"S:=65535

Line 1: This is the file header, it says that this is an APX file and that the version is 1.2 (current version).

Line 2: The letter N represents an APX Node line. The name of the node is "Sender". Note that in APX we use the term *node* to represent software components.

Line 3: The letter P represents a provide port line. The name of the port is VehicleSpeed and its type is uint16. The initial value is 65535.

Line 4: This is anohter provide port line. This one has the name EngineSpeed and its type is also uint16. The initial value is 65535.

Similarly, the Receiver component has two require ports and can be represented in APX Text as follows::

   APX/1.2
   N"Receiver"
   R"VehicleSpeed"S:=65535
   R"EngineSpeed"S:=65535

Port Lines
----------

.. image:: _static/APX_PortSignature.png

Port lines consists of several parts where the most important bit is the port signature. The port signature consists of the port name followed by its
data signature. Each port line has an optional port attribute section after the data signature.
Port attributes are most often used to set the initial value of the port but can also be used to set queued port attributes as well as parameter attributes.

Examples:

+-----------------------------+-----------+-------------------------+----------------+-----------------+
| Port Line                   | Port Type |   Port Signature        | Data Signature | Port Attributes |
+=============================+===========+=========================+================+=================+
| P"VehicleSpeed"S:=65535     | Provide   | "VehicleSpeed"S         | S              | =65535          |
+-----------------------------+-----------+-------------------------+----------------+-----------------+
| R"EngineSpeed"S:=65535      | Require   | "EngineSpeed"S          | S              | =65535          |
+-----------------------------+-----------+-------------------------+----------------+-----------------+
| P"ParkBrakeStatus"C(0,3):=3 | Provide   | "ParkBrakeStatus"C(0,3) | C(0,3)         | =3              |
+-----------------------------+-----------+-------------------------+----------------+-----------------+

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

Each primitive type character may be optionally followed by the characters "[n]" where n is the array length (repeat count).
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




