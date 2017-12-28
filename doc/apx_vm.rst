APX Virtual Machine
===================

Opcode Table
------------

+---------------+---------------+-------------------------------------------------+--------------------------+
| Opcode Number | Opcode Name   | Opcode arguments (additional bytes)             | Description              |
+===============+===============+=================================================+==========================+
| 0             |    NOP        |                                                 | No operation             |
+---------------+---------------+-------------------------------------------------+--------------------------+
| 1             |  PROG_HEADER  | 1. progTypeByte: (0)=pack, (1)=unpack           | program header           |
|               |               | 2. variantTypeByte (see below)                  |                          |
|               |               | 3. lengthByte1 (MSB)                            |                          |
|               |               | 4. lengthByte2                                  |                          |
|               |               | 5. lengthByte3 (LSB)                            |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  2            | PACK_U8       |                                                 | pack single uint8        |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  3            | PACK_U16      |                                                 | pack single uint16       |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  4            | PACK_U32      |                                                 | pack single uint32       |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  5            | PACK_S8       |                                                 | pack single sint8        |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  6            | PACK_S16      |                                                 | pack single sint16       |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  7            | PACK_S32      |                                                 | pack single sint32       |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  8            | PACK_STR      | 1. LengthByte1(MSB)                             | pack string              |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  9            | PACK_U8AR     | 1. LengthByte1(MSB)                             | pack uint8 array         |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  10           | PACK_U16AR    | 1. LengthByte1(MSB)                             | pack uint16 array        |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  15           | UNPACK_U8     |                                                 | unpack single uint8      |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  16           | UNPACK_U16    |                                                 | unpack single uint16     |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  17           | UNPACK_U32    |                                                 | unpack single uint32     |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  18           | UNPACK_S8     |                                                 | unpack single sint8      |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  19           | UNPACK_S16    |                                                 | unpack single sint16     |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  20           | UNPACK_S32    |                                                 | unpack single sint32     |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  21           | UNPPACK_STR   | 1. LengthByte1(MSB)                             | unpack string            |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  22           | UNPACK_U8AR   | 1. LengthByte1(MSB)                             | unpack uint8 array       |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  23           | UNPACK_U16AR  | 1. LengthByte1(MSB)                             | unpack uint16 array      |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  24           | UNPACK_U32AR  | 1. LengthByte1(MSB)                             | unpack uint32 array      |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  25           | UNPACK_S8AR   | 1. LengthByte1(MSB)                             | unpack sint8 array       |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  26           | UNPACK_S16AR  | 1. LengthByte1(MSB)                             | unpack sint16 array      |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  27           | UNPACK_S32AR  | 1. LengthByte1(MSB)                             | unpack sint32 array      |
|               |               | 2. LengthByte1(LSB)                             |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  28           | RECORD_ENTER  |                                                 | record inside of record  |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  29           | RECORD_SELECT | null-terminated utf-8 string                    | name of record element   |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  30           | RECORD_LEAVE  |                                                 |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  31           | ARRAY_ENTER   |                                                 | Used only for array of   |
|               |               |                                                 | records                  |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  32           | ARRAY_NEXT    |                                                 |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+
|  33           | ARRAY_LEAVE   |                                                 |                          |
+---------------+---------------+-------------------------------------------------+--------------------------+

APX Variants
------------

Variants are variables that can store values of different types. They are supported in one way or another in most programming languages.

**Types of variants:**

- Scalars (integers, strings)
- Lists (list of variants)
- Maps (key-value map to variants)

Variant types are identified internally using integers according to the following table:

+-------+---------------+
| Value |     Name      |
+=======+===============+
| -1    | VTYPE_INVALID |
+-------+---------------+
| 0     | VTYPE_SCALAR  |
+-------+---------------+
| 1     | VTYPE_LIST    |
+-------+---------------+
| 2     | VTYPE_MAP     |
+-------+---------------+

Variant Language Mapping
~~~~~~~~~~~~~~~~~~~~~~~~

Each APX implementation maps the APX variant according to what is available to the language. The following table shows how the mapping is done for languages that implements APX.

+---------------------------+--------------+--------------+----------------------+
| Programming Language      | VTYPE_SCALAR | VTYPE_LIST   | VTYPE_MAP            |
+===========================+==============+==============+======================+
| C (with dtl_type library) | dtl_sv_t     | dtl_av_t     | dtl_hv_t             |
+---------------------------+--------------+--------------+----------------------+
| C++ (with Qt variants)    | QVariant     | QVariantList | QVariantMap          |  
+---------------------------+--------------+--------------+----------------------+
| Python                    | (int, str)   | list         | dict                 |
+---------------------------+--------------+--------------+----------------------+
| Visual Basic (Excel)      | Variant      | Variant      | Scripting.Dictionary |
+---------------------------+--------------+--------------+----------------------+

Opcode Details
--------------

PROG_HEADER
~~~~~~~~~~~

The program header opcode is the first instruction of a program. It indicates what kind of program it is and what kind of data it operates on.

**progTypeByte:** What kind of program is this? (0)=pack, (1)=unpack.

**variantTypeByte:** What value type is expected? (-1)=VTYPE_INVALID, (0)=VTYPE_SCALAR, (1)=VTYPE_LIST, (2)=VTYPE_MAP

**length:** Number of raw bytes this programs uses to pack/unpack the variant data. This is stored as a 24-bit integer using big endian byte order.



