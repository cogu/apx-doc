RemoteFile 1.0 (draft)
======================

.. toctree::
   :maxdepth: 2



.. highlight:: none

RemoteFile is a protocol used by two nodes in a point-to-point communication link (e.g. a TCP socket).
It's primary use case is to synchronize serialized objects (byte arrays) from one node to another but it can potentially be used for any content.

RemoteFile uses a publish/subscribe pattern where the first node (called the local node) publishes a file which the other node (called the remote node) can choose to open.
If the remote node opens the file then the following things will happen:

   1. The local node (the publisher) will initially send the entire file to the remote node (the subscriber).
   2. The local node then sets up a subscription scheme of sorts, allowing it to partially update the file using write commands (delta-copy commands).
   3. The local node stops sending file updates to the remote node if the remote node closes the file (or if the remote node disconnects).

The initial file transfer and delta-copy are unidirectional (data is sent from the publisher to the subscriber).
This means that the remote node can never write back (update) the file in the local nodes memory.
However, RemoteFile itself is a bi-directional protocol meaning that both nodes can send files to each other.

Files in the RemoteFile layer are just memory mappped byte arrays with:

  1. An associated name (e.g. "myfile.txt").
  2. An associated (fixed) length (e.g. 100 bytes).
  3. A (virtual) start address) where the file is mapped (what this means will be explained later).

Example
--------
Computer 1 wants to send the time of day as an ASCII string to Computer 2 using the following format::

   hh:mm:ss

(For simplicity, let's assume a 24h clock.)

In addition, computer 1 will send an updated time string to computer 2 (using delta-copy) once every second.

In this scenario, computer 1 is the local node and computer 2 is the remote node. The remote node connects to the local node using TCP.
   
The string will require 8 characters to represent.

  +--------+----------------+--------+
  | offset | description    | value  |
  +========+================+========+
  | 0      |  hours (tens)  |   0-2  |
  +--------+----------------+--------+
  | 1      |  hours (ones)  |   0-3  |
  +--------+----------------+--------+
  | 2      | (fixed char)   |    :   |
  +--------+----------------+--------+
  | 3      | minutes (tens) |  0-5   |
  +--------+----------------+--------+
  | 4      | minutes (ones) |  0-9   |
  +--------+----------------+--------+
  | 5      | (fixed char)   |   :    |
  +--------+----------------+--------+
  | 6      | seconds (tens) |   0-5  |
  +--------+----------------+--------+
  | 7      | seconds (ones) |   0-9  |
  +--------+----------------+--------+

Min::

  00:00:00
  
Max::
  
  23:59:59



Init mode
~~~~~~~~~

   1. The remote node (computer 2) connects to the local node (using a TCP socket).
   2. The local node (computer 1) sends a FileInfo struct to remote node containing a file name (name="time.txt") and a file length (length=8).
   3. The remote node sends an OpenFile struct back to the local node, requesting to open the file "time.txt".
   4. Local node sends current content of "time.txt" to the remote node (8 bytes).
   
For this example, let's assume that the content of "time.txt" during initial transfer in step 4 had the following content::

   12:34:56

Delta-copy mode
~~~~~~~~~~~~~~~

Let's say we want to save bandwith in the communication link and send as few bytes as possible.
This can be acheived by delta copying changes from the local nodes version of "time.txt" to the remote node's copy of "time.txt".

::
   
   12:34:56 => 12:34:57
   
Only the last character (offset 7) has changed, send delta copy command with length 1:

::
  
  offset:7,
  len:1,
  data:"7"

------------

::
   
   12:34:59 => 12:35:00

When the seconds value changes from 59 to 00 then minutes increases from 34 to 35.
This can be sent as delta-copy in two different ways:

------------

::
  
   offset:4,
   len:4,
   data:"5:00"
  
or

::

   offset:4,
   len:1,
   data:"5"
   
directly followed by:

::

   offset:6,
   len:2,
   data:"00"
  
In this case, the first form is recommended since it uses less overhead bytes even though we overwrite the ':' character with the same value.

**Note:** This example is used to demonstrate the RemoteFile protocol only. Using ASCII strings to send time values between two computers is neither common or very efficient.

Basic Concepts
--------------

Message based communication
~~~~~~~~~~~~~~~~~~~~~~~~~~~

RemoteFile depends on a lower layer protocol that can send messages. A message has two components:

   1. A message header containing the length of the message.
   2. A message body containing the message data (sometimes called the message payload).
   
Since RemoteFile is designed to be used on all kinds of communication links (TCP, websockets, CAN, SPI etc.) it
does not officially define a message header since there usually exists protocols for this already.

In case you do not have a message passing protocol in place but you do have a stream based communication link (like a TCP socket) you can use NumHeader_.

If you plan to use RemoteFile on TCP then NumHeader32_ is the recomended choice.

The address space
~~~~~~~~~~~~~~~~~

RemoteFile defines a virtual address range of 1GiB (0 - 2^30-1 bytes). In this space the user can map a file (giving it a start address) of any size as long as:

   1. The file's start address + file length is within the 1GiB address boundary.
   2. The file's start address + file length does not collide with an already mapped file.

Each node of the (point-to-point) communication link defines its own 1GiB address range.
Files mapped by node A belongs to the address range of node A. File mapped by node B belongs to the address range of node B.

There is a special file mapped to the last 1024 bytes of the 1GiB range of each node.
This file is always open and node A uses it to send open/close requests into node B's memory while node B uses it to send open/close requests in nodes A memory.

From node A's perspective, node A is the local node and node B is the remote node. From nodes B's perspective, node B is the local node and node A is the remote node.


RemoteFile messages
-------------------

A local node can at any time write anywhere in the 1GiB address range of the remote node's memory map under these conditions:

   1. There is a file mapped at the address of the write.
   2. The file in question is currently open (the remote node has previously sent a request to open the file).


A write message has the following format::
     
   write_msg: address_header data
   address_header: see below
   data: byte*

The length of *data* can be calculated as: length(*write_msg*) - length(*address_header*)
where length(*write_msg*) needs to be specified by an underlying protocol (see NumHeader_) and length(*address_header*)
can be either 2 or 4 bytes depending on the most significant bit of the first byte of *address_header* (see definition of :ref:`address_header`).

Writing data into remote memory
-------------------------------

Writing data into the 1GiB memory of the remote node is the only allowed message type in the remotefile protocol (after the initial greeting message has been sent/acknowledged).
Special operations (called commands) are written to a special file located in the last 1024 bytes of the address space.

There are 4 types of messaging formats that can be employed by the protocol when it needs to write data to remote memory:

   * Short length & Low address
   * Long length & Low address
   * Short length & High address
   * Long length & High address

Short length & Low address
~~~~~~~~~~~~~~~~~~~~~~~~~~

**When to Use:** Writing 0-127 bytes with start address 0-16383.

**Message Layout:**

.. rst-class:: table-numbers

   +------+---------------------+--------+---------------------------+
   | Byte |    Protocol         | Value  |       Meaning             |
   +======+=====================+========+===========================+
   | 0    | NumHeader (16/32)   |  0-127 |  Length of message        |
   +------+---------------------+--------+---------------------------+
   | 1    |  RemoteFile         | 0-255  | Start address (high byte) |
   +------+---------------------+--------+---------------------------+
   | 2    | RemoteFile          | 0-255  | Start address (low byte)  |
   +------+---------------------+--------+---------------------------+
   | 3    | Application data    | 0-255  | Payload  (e.g. APX data)  |
   +------+---------------------+--------+---------------------------+
   | ...  |   ...               | ...    | ...                       |
   +------+---------------------+--------+---------------------------+

Long length & Low address
~~~~~~~~~~~~~~~~~~~~~~~~~

**When to Use:** Writing 128 bytes or more with start address 0-16383.

**Message Layout:**

.. rst-class:: table-numbers

   NumHeader16:
   
   +------+---------------------+-----------+--------------------------------+
   | Byte |    Protocol         | Value     |       Meaning                  |
   +======+=====================+===========+================================+
   | 0    | NumHeader16         | 0x80-0xFF |  Length of message (high byte) |
   +------+---------------------+-----------+--------------------------------+
   | 1    | NumHeader16         | 0x00-0xFF |  Length of message (low byte)  |
   +------+---------------------+-----------+--------------------------------+
   | 2    | RemoteFile          | 0-255     | Start address (high byte)      |
   +------+---------------------+-----------+--------------------------------+
   | 3    | RemoteFile          | 0-255     | Start address (low byte)       |
   +------+---------------------+-----------+--------------------------------+
   | 4    | Application data    | 0-255     | Payload  (e.g. APX data)       |
   +------+---------------------+-----------+--------------------------------+
   | ...  |   ...               | ...       | ...                            |
   +------+---------------------+-----------+--------------------------------+

   NumHeader32:

   +------+---------------------+-----------+---------------------------+
   | Byte |    Protocol         | Value     |       Meaning             |
   +======+=====================+===========+===========================+
   | 0    | NumHeader32         | 0x80-0xFF |  Length of message (MSB)  |
   +------+---------------------+-----------+---------------------------+
   | 1    | NumHeader32         | 0x00-0xFF |  Length of message        |
   +------+---------------------+-----------+---------------------------+
   | 2    | NumHeader32         | 0x00-0xFF |  Length of message        |
   +------+---------------------+-----------+---------------------------+
   | 3    | NumHeader32         | 0x00-0xFF |  Length of message (LSB)  |
   +------+---------------------+-----------+---------------------------+
   | 4    | RemoteFile          | 0-255     | Start address (high byte) |
   +------+---------------------+-----------+---------------------------+
   | 5    | RemoteFile          | 0-255     | Start address (low byte)  |
   +------+---------------------+-----------+---------------------------+
   | 6    | Application data    | 0-255     | Payload  (e.g. APX data)  |
   +------+---------------------+-----------+---------------------------+
   | ...  |   ...               | ...       | ...                       |
   +------+---------------------+-----------+---------------------------+

Short length & High address
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**When to Use:** Writing 0-127 bytes with start address 16384 or higher.

**Message Layout:**

.. rst-class:: table-numbers

   +------+---------------------+--------+--------------------------+
   | Byte |    Protocol         | Value  |       Meaning            |
   +======+=====================+========+==========================+
   | 0    | NumHeader (16/32)   |  0-127 |  Length of message       |
   +------+---------------------+--------+--------------------------+
   | 1    | RemoteFile          | 0-255  | Start address (MSB)      |
   +------+---------------------+--------+--------------------------+
   | 2    | RemoteFile          | 0-255  | Start address            |
   +------+---------------------+--------+--------------------------+
   | 3    | RemoteFile          | 0-255  | Start address            |
   +------+---------------------+--------+--------------------------+
   | 4    | RemoteFile          | 0-255  | Start address (LSB)      |
   +------+---------------------+--------+--------------------------+
   | 5    | Application data    | 0-255  | Payload (e.g. APX data)  |
   +------+---------------------+--------+--------------------------+
   | ...  |   ...               | ...    | ...                      |
   +------+---------------------+--------+--------------------------+

Long length & High address
~~~~~~~~~~~~~~~~~~~~~~~~~~

**When to Use:** Writing 128 bytes or more with start address 16384 or higher.

**Message Layout:**

.. rst-class:: table-numbers

   NumHeader16:
   
   +------+---------------------+-----------+--------------------------------+
   | Byte |    Protocol         | Value     |       Meaning                  |
   +======+=====================+===========+================================+
   | 0    | NumHeader16         | 0x80-0xFF |  Length of message (high byte) |
   +------+---------------------+-----------+--------------------------------+
   | 1    | NumHeader16         | 0x00-0xFF |  Length of message (low byte)  |
   +------+---------------------+-----------+--------------------------------+
   | 1    | RemoteFile          | 0-255     | Start address (MSB)            |
   +------+---------------------+-----------+--------------------------------+
   | 2    | RemoteFile          | 0-255     | Start address                  |
   +------+---------------------+-----------+--------------------------------+
   | 3    | RemoteFile          | 0-255     | Start address                  |
   +------+---------------------+-----------+--------------------------------+
   | 4    | RemoteFile          | 0-255     | Start address (LSB)            |
   +------+---------------------+-----------+--------------------------------+
   | 4    | Application data    | 0-255     | Payload  (e.g. APX data)       |
   +------+---------------------+-----------+--------------------------------+
   | ...  |   ...               | ...       | ...                            |
   +------+---------------------+-----------+--------------------------------+

   NumHeader32:
   
   +------+---------------------+-----------+---------------------------+
   | Byte |    Protocol         | Value     |       Meaning             |
   +======+=====================+===========+===========================+
   | 0    | NumHeader32         | 0x80-0xFF |  Length of message (MSB)  |
   +------+---------------------+-----------+---------------------------+
   | 1    | NumHeader32         | 0x00-0xFF |  Length of message        |
   +------+---------------------+-----------+---------------------------+
   | 2    | NumHeader32         | 0x00-0xFF |  Length of message        |
   +------+---------------------+-----------+---------------------------+
   | 3    | NumHeader32         | 0x00-0xFF |  Length of message (LSB)  |
   +------+---------------------+-----------+---------------------------+
   | 4    | RemoteFile          | 0-255     | Start address (MSB)       |
   +------+---------------------+-----------+---------------------------+
   | 5    | RemoteFile          | 0-255     | Start address             |
   +------+---------------------+-----------+---------------------------+
   | 6    | RemoteFile          | 0-255     | Start address             |
   +------+---------------------+-----------+---------------------------+
   | 7    | RemoteFile          | 0-255     | Start address (LSB)       |
   +------+---------------------+-----------+---------------------------+
   | 8    | Application data    | 0-255     | Payload  (e.g. APX data)  |
   +------+---------------------+-----------+---------------------------+
   | ...  |   ...               | ...       | ...                       |
   +------+---------------------+-----------+---------------------------+


.. _address_header:

Address Header
--------------

The *address_header* can have two forms: low and high address form (similar to short/long form of NumHeader_).

address_header - low address form (0-16383)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This form uses a 16-bit integer encoded in big endian byte order (U16BE)

.. rst-class:: table-numbers

   +----------+----------+----------+------------+
   |          Byte #1               | Byte #2    |
   +==========+==========+==========+============+
   |   BIT 7  |   BIT 6  | BITS 5-0 | BITS 7-0   |
   +----------+----------+----------+------------+ 
   | HIGH_BIT | MORE_BIT |      ADDRESS          |
   +----------+----------+----------+------------+ 
   |    0     |   0-1    |       0-16383         |
   +----------+----------+----------+------------+

address_header - high address form (16384-2^30-1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This form uses a 32-bit integer encoded in big endian byte order (U32BE)

.. rst-class:: table-numbers

   +----------+----------+----------+-----------+----------+----------+
   |          Byte #1               | Byte #2   | Byte #3  | Byte #4  |
   +==========+==========+==========+===========+==========+==========+
   |   BIT 7  |   BIT 6  | BITS 5-0 | BITS 7-0  | BITS 7-0 | BITS 7-0 |
   +----------+----------+----------+-----------+----------+----------+  
   | HIGH_BIT | MORE_BIT |              ADDRESS                       |
   +----------+----------+----------+-----------+----------+----------+ 
   |    1     |   0-1    |              16384-2^30-1                  |
   +----------+----------+----------+-----------+----------+----------+

address_header flags
~~~~~~~~~~~~~~~~~~~~~

HIGH_BIT
^^^^^^^^

when set to 0, the AdressHeader is 2 bytes in length and it uses a 14-bit address range (0-16383).
This saves 2 bytes on every write which is significant if only 1 data byte is to be updated in a file.

When set to 1, the address_header is 4 bytes in length and the whole address range of 1GiB can be written to.

.. note::

   You should try to map files that changes its data frequently into the first 16KiB of the address range.
   Files that changes rarely (or not at all) should be mapped anywhere else.
   
MORE_BIT
^^^^^^^^
This bit indicates that more data is to be sent before notifying upper layers.
This is used for large data transfers where the entire file (or file update) could not fit into a single message.
The bit is set to 1 for all data packets (messages) except the last one (where it is set 0). When the 0 is seen the entire message can be parsed by upper application layers as a single (atomic) write.

Example
^^^^^^^

.. rst-class:: table-numbers

   +------------+-------------+------------------------+
   |   Address  | MORE_BIT    |   Packed Data          |
   +============+=============+========================+
   |     0      |  0 (false)  | ``"\x00\x00"``         |
   +------------+-------------+------------------------+
   |     0      |  1 (true)   | ``"\x40\x00"``         |
   +------------+-------------+------------------------+
   |   16383    |  0 (false)  | ``"\x3F\xFF"``         |
   +------------+-------------+------------------------+
   |   16383    |  1 (true)   | ``"\x7F\xFF"``         |
   +------------+-------------+------------------------+
   |   16384    |  0 (false)  | ``"\x80\x00\x40\x00"`` |
   +------------+-------------+------------------------+
   |   16384    |  1 (false)  | ``"\xC0\x00\x40\x00"`` |
   +------------+-------------+------------------------+
   | 1073741823 |  0 (false)  | ``"\xBF\xFF\xFF\xFF"`` |
   +------------+-------------+------------------------+
   | 1073741823 |  1 (false)  | ``"\xFF\xFF\xFF\xFF"`` |
   +------------+-------------+------------------------+

RemoteFile commands
-------------------

The last 1024 bytes of the 1GiB address range is a special file. It starts at address ``0x3FFFFC00`` and ends on address ``0x3FFFFFFFF``.
When writing to this file you must always use adddress ``0x3FFFFC00`` (this is the only acceptable write address of this area).

The smallest acceptable data length when writing to this area is 1 byte, the longest is 1024 bytes.

In this special file area you send command data structures. These are:

  * FileInfo - Information about a file (it's name, length and start address).
  * FileRevoke - Opposite of a FileInfo, unmaps a file from the address area. 
  * FileOpen - Used as request to open a file
  * FileClose - Used as request to close a file

Node A can send one or more FileInfo structures to Node B telling B what files A has mapped into
its memory (``0x0-0x3FFFFBFF``). Conversely, B sends its FileInfo structures to A telling A what files 
B has mapped into its memory.

When FileInfo structures have arrived to node A (sent by node B), A can now send a FileOpen structure to B
requesting to open the file. If Node B accepts, it sends the file content to A by writing to
the start address of the file that was opened. The same principle applies to node B where node B can
send a FileOpen request to node A with the start address of the file that B wants to open.

Closing a file is done by sending a FileClose structure to the command area (``0x3FFFFC00``) containing
the start address of the file you want to close.
  
  
.. rst-class:: table-numbers
   
   +---------------------+---------+
   |   CmdType           |  Value  |
   +=====================+=========+
   | RMF_CMD_ACK         |    0    |
   +---------------------+---------+
   | RMF_CMD_NACK        |    1    |
   +---------------------+---------+
   | RMF_CMD_FILE_INFO   |    3    |
   +---------------------+---------+
   | RMF_CMD_REVOKE_FILE |    4    |
   +---------------------+---------+
   | RMF_CMD_FILE_OPEN   |    10   |
   +---------------------+---------+
   | RMF_CMD_FILE_CLOSE  |    11   |
   +---------------------+---------+

Command data structures
-----------------------

Acknowledge
~~~~~~~~~~~

.. rst-class:: table-numbers
   
   +--------+------------+--------+---------------------+----------------------------------------------------+
   | Offset |    Name    | Type   |  Value              |   Description                                      |
   +========+============+========+=====================+====================================================+
   |   0    |  cmdType   |  U32LE | RMF_CMD_ACK         |   Command type                                     |
   +--------+------------+--------+---------------------+----------------------------------------------------+
   
FileInfo (length: 48-1024 bytes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both sides of the communication link sends zero or more FileInfo structs (one per file) informing the other side which files it currently has available (mapped into memory).
The length of the struct is 48 bytes + the length of the file name which is the last part of the struct.

Since the longest message that can be sent to the special file area is 1024 bytes, the longest possible file name is 975 bytes (1 byte reserved for the null terminator).

Regarding the Type column: The term "LE" means little endian byte order.

.. note::

   The byte order used in command data structures will be possible to select later on using the greeting header. This is not yet specified.

.. rst-class:: table-numbers
   
   +--------+--------------+--------+-------------------+----------------------------------------------+
   | Offset |    Name      | Type   |     Value         | Description                                  |
   +========+==============+========+===================+==============================================+
   |   0    |  cmdType     |  U32LE | RMF_CMD_FILE_INFO |   Command type                               |
   +--------+--------------+--------+-------------------+----------------------------------------------+
   |   4    |  address     |  U32LE |     0-2^30        |   Start-address of the memory mapped file    |
   +--------+--------------+--------+-------------------+----------------------------------------------+
   |   8    |  length      |  U32LE |     0-2^30        |  (maximum) length of the file                |
   +--------+--------------+--------+-------------------+----------------------------------------------+
   |   12   | fileType     | U16LE  |      0-2          |  Type of file, see below                     |
   +--------+--------------+--------+-------------------+----------------------------------------------+
   |   14   | digestType   |  U16LE |      0-1          |   Type of checksum, see below                |
   +--------+--------------+--------+-------------------+----------------------------------------------+
   |   16   | digestData   | U8[32] |     0-255         | placeholder bytes for digestData (checksum)  |
   +--------+--------------+--------+-------------------+----------------------------------------------+
   |  48    | name         | string | ``[0-9a-zA-Z_]``  | file name as a null terminated C string      |
   +--------+--------------+--------+-------------------+----------------------------------------------+
   
   **fileType:**
   
   * 0 - memory mapped file with fixed length (default)
   * 1 - memory mapped file with dynamic length (to be implemented)
   * 2 - chunk in a file stream (to be implemented)
   
   **digestType:**
   
   * 0 - no digest, digestData array is filled with zeros (default)
   * 1 - SHA1 digest (as generated by sha1sum). Unused bytes are padded with zeros from the right.
   * 2 - SHA256 digest (as generated by sha256sum)
   
**Example:**

.. rst-class:: table-numbers

   +--------+--------------+-----------------------+------------------------+
   | Offset |    Name      |     Value             | Packed data            |
   +========+==============+=======================+========================+
   |   0    |  cmdType     | RMF_CMD_FILE_INFO     | ``"\x03\x00\x00\x00"`` |
   +--------+--------------+-----------------------+------------------------+
   |   4    |  address     |     0x12345678        | ``"\x78\x56\x34\x12"`` |
   +--------+--------------+-----------------------+------------------------+
   |   8    |  length      |     1000              | ``"\xe8\x03"``         |
   +--------+--------------+-----------------------+------------------------+
   |   12   | fileType     |        0              | ``"\x00\x00"``         |
   +--------+--------------+-----------------------+------------------------+
   |   14   | digestType   |        0              | ``"\x00\x00"``         |
   +--------+--------------+-----------------------+------------------------+
   |   16   | digestData   | ``"\x00\x00...\x00"`` | ``"\x00\x00...\x00"``  |
   +--------+--------------+-----------------------+------------------------+
   |  48    | name         |  ``"file1.txt"``      | ``"file1.txt\0"``      |
   +--------+--------------+-----------------------+------------------------+  

FileRevoke (length: 8 bytes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. rst-class:: table-numbers
   
   +--------+------------+--------+---------------------+----------------------------------------------------+
   | Offset |    Name    | Type   |  Value              |   Description                                      |
   +========+============+========+=====================+====================================================+
   |   0    |  cmdType   |  U32LE | RMF_CMD_FILE_REVOKE |   Command type                                     |
   +--------+------------+--------+---------------------+----------------------------------------------------+
   |   4    |  address   |  U32LE |     0-2^30          |   Start-address of the memory mapped file to revoke|
   +--------+------------+--------+---------------------+----------------------------------------------------+

   
FileOpen (length: 8 bytes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. rst-class:: table-numbers
   
   +--------+--------------+--------+-------------------+----------------------------------------------------+
   | Offset |    Name      | Type   |  Value            |   Description                                      |
   +========+==============+========+===================+====================================================+
   |   0    |  cmdType     |  U32LE | RMF_CMD_FILE_OPEN |   Command type                                     |
   +--------+--------------+--------+-------------------+----------------------------------------------------+
   |   4    |  address     |  U32LE |     0-2^30        |   Start-address of the memory mapped file to open  |
   +--------+--------------+--------+-------------------+----------------------------------------------------+

FileClose (length: 8 bytes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. rst-class:: table-numbers
   
   +--------+--------------+--------+--------------------+-----------------------------------------------------+
   | Offset |    Name      | Type   |     Value          |   Description                                       |
   +========+==============+========+====================+=====================================================+
   |   0    |  cmdType     |  U32LE | RMF_CMD_FILE_CLOSE |   Command type                                      |
   +--------+--------------+--------+--------------------+-----------------------------------------------------+
   |   4    |  address     |  U32LE |     0-2^30         |   Start-address of the memory mapped file to close  |
   +--------+--------------+--------+--------------------+-----------------------------------------------------+

RemoteFile greeting message
---------------------------

When a client connects to a server, it sends out a single greeting message which tells which version of RemoteFile it supports
followed by zero or more headers followed by an empty line (a single newline character). This is done once per connection.
The greeting message is prepended by a normal message header (such as NumHeader16 or NumHeader32).
If NumHeader is used before greeting message, it is strongly recommended that the greeting message itself is less than or equal to 127 characters.
This is because the short forms of both NumHeader16 and NumHeader32 are identical.

If the RemoteFile server accepts the greeting message it responds with a single acknowledge command.
The client must wait for the acknowledge from the server before sending any further messages.
After the acknowledge has been sent to the client, both server and client is allowed to send remotefile write messages to the each other.

::

   remotefile_client: greeting write_msg*
   remotefile_server: acknowledge write_msg*
   greeting: "RMFP/1.0\n" header* "\n"
   header: "[_A-Za-z][_\-A-Za-z0-9]+" : "[_\-A-Za-Z0-9]+" "\n"
   write_msg: address_header msg_data
   msg_data: byte*
   
   
   

For address_header definition see address_header_

Greeting Headers
~~~~~~~~~~~~~~~~

**NumHeader-Format**

This header indicates which NumHeader format is used. Valid values are *16* and *32*.
   
   
NumHeader
---------
NumHeader encodes an integer in big endian, or network byte order. This integer is used as the message length (the message header).
The integer is parsed first, which tells you how many bytes the message is. Then you wait until that number of bytes has arrived until you start parsing the message.

The most significant bit of the first byte is called the LONG_BIT. When the bit is set it uses long form, when the bit is 0 it uses short form.

NumHeader16
~~~~~~~~~~~

NumHeader16 uses 1 byte in short form and 2 bytes in long form. It can encode integers in the range 0-32895.

**NumHeader16 - short form (0-127)**:

.. rst-class:: table-numbers

   +-----------+-----------+
   | Byte #1               | 
   +===========+===========+
   |   BIT 7   |  BITS 6-0 | 
   +-----------+-----------+
   | LONG_BIT  |   VALUE   |
   +-----------+-----------+
   |     0     |   0-127   |
   +-----------+-----------+

**NumHeader16 - long form (values 128-32767)**:

.. rst-class:: table-numbers

   +-----------+----------+-------------+
   | Byte #1              | Byte #2     | 
   +===========+==========+=============+
   |   BIT 7   | BITS 6-0 | BITS 7-0    |
   +-----------+----------+-------------+
   | LONG_BIT  |      VALUE             |
   +-----------+----------+-------------+
   |     1     | 128-32767 (big endian) |
   +-----------+----------+-------------+


.. note::

  When LONG_BIT=1 the values 0-127 can be considered to be an invalid range (since you would normally have used the short form instead).
  This means that you can reinterpret the range n=0-127 as 32768+n, raising the threshold of the maximum message length to 32768+127=32895 bytes.
  
  This can be seen as an extension to NumHeader16.


NumHeader32
~~~~~~~~~~~

NumHeader32 uses 1 byte in short form and 4 bytes in long form. It can encode integers in the range 0-2147483647.
The short form of NumHeader32 is identical to the short form of NumHeader16.

**NumHeader32 - short form (0-127)**:

.. rst-class:: table-numbers

   +-----------+-----------+
   | Byte #1               | 
   +===========+===========+
   |   BIT 7   |  BITS 6-0 | 
   +-----------+-----------+
   | LONG_BIT  |   VALUE   |
   +-----------+-----------+
   |     0     |   0-127   |
   +-----------+-----------+

**NumHeader32 - long form (values 128-2147483647)**:

.. rst-class:: table-numbers

   +-----------+----------+----------+----------+----------+
   |         Byte #1      | Byte #2  | Byte #3  | Byte #4  |
   +===========+==========+==========+==========+==========+
   |   BIT 7   | BITS 6-0 | BITS 7-0 | BITS 7-0 | BITS 7-0 | 
   +-----------+----------+----------+----------+----------+
   | LONG_BIT  |            VALUE                          |
   +-----------+----------+----------+----------+----------+
   |     1     |           128-2147483647 (big endian)     |
   +-----------+----------+----------+----------+----------+

NumHeader Examples 
~~~~~~~~~~~~~~~~~~   
      
.. rst-class:: table-numbers
  
   +------------+----------------+------------------------+
   |   Value    | NumHeader16    | NumHeader32            |
   +============+================+========================+
   |     0      | ``"\x00"``     | ``"\x00"``             |
   +------------+----------------+------------------------+
   |    127     | ``"\x7F"``     | ``"\x7F"``             |
   +------------+----------------+------------------------+
   |    128     | ``"\x80\x80"`` | ``"\x80\x00\x00\x80"`` |
   +------------+----------------+------------------------+
   |   32767    | ``"\xFF\FF"``  | ``"\x80\x00\x7F\xFF"`` |
   +------------+----------------+------------------------+ 
   |   32768    | ``"\x80\00"``  | ``"\x80\x00\x80\x00"`` |
   +------------+----------------+------------------------+ 
   |   32895    | ``"\x80\7F"``  | ``"\x80\x00\x80\x7F"`` |
   +------------+----------------+------------------------+
   | 2147483647 |  --            | ``"\xFF\xFF\xFF\xFF"`` |
   +------------+----------------+------------------------+
   
   The table above demonstrates how (integer) values are represented in binary form using string literals.
   These literals are valid C99 strings (compiles in both C(99) and C++).
   
   In python you will need to prepend the string literal with the character ``b``.   
   
   Example: ``"\x80\x80"`` -->  ``b"\x80\x80"``
   
