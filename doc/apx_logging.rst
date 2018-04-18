APX Logging
===========

Version: 0.1 (draft)

APX logging can be enabled in the APX server from a client connection.
To enable logging the client need to do two things.

1. Send the Logging Enable command using the :doc:`remotefile` protocol.
2. Publish a new file called *apx.log* as a file info command using the :doc:`remotefile` protocol.

It's important the the file *apx.log* has the file-type set to stream in the file info struct sent by client.

When logging has been enabled, the APX server will try to open the apx.log file published by the client.
Once apx.log has been succesfully opened, the APX server will start to deliver events by writing into the stream file apx.log.

In addition, the APX server will start to publish all APX files (APX definitions, input data files, output data files) to the client.
All APX-related files are implicitly set to state **open** by server. In other words, the client does not explicitly need to send file open commands to the server.

Event Definitions
-----------------

These are the events that the server will write into the apx.log file stream.

Encoding: U32LE (uint32, Little Endian)

.. rst-class:: table-numbers

+---------------------------------+--------+
| Event Type                      | Value  |
+=================================+========+
| `APX_EVENT_NEW_CONNECTION`_     | 0      |
+---------------------------------+--------+
| `APX_EVENT_DISCONNECTED`_       | 1      |
+---------------------------------+--------+
| `APX_EVENT_ADD_NODE`_           | 2      |
+---------------------------------+--------+
| `APX_EVENT_REMOVE_NODE`_        | 3      |
+---------------------------------+--------+

APX_EVENT_NEW_CONNECTION
~~~~~~~~~~~~~~~~~~~~~~~~

TBD

APX_EVENT_DISCONNECTED
~~~~~~~~~~~~~~~~~~~~~~

TBD

APX_EVENT_ADD_NODE
~~~~~~~~~~~~~~~~~~

TBD

APX_EVENT_REMOVE_NODE
~~~~~~~~~~~~~~~~~~~~~~

TBD
