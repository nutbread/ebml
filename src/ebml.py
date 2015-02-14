# Imports
import re, sys, math, struct, datetime;
version_info = ( 1 , 0 );



# Multi versioning
if (sys.version_info[0] == 3):
	# Version 3
	def py_2or3_byte_to_int(value):
		return value;
	def py_2or3_int_to_byte(value):
		return bytes([ value ]);
	def py_2or3_intlist_to_bytes(value):
		return bytes(value);
	def py_2or3_byte_ord(char):
		return char;
	def py_2or3_var_is_bytes(value):
		return isinstance(value, bytes);
	def py_2or3_var_is_unicode(value):
		return isinstance(value, str);
	def py_2or3_var_is_integer(v):
		return isinstance(v, int);
	def py_2or3_var_is_string(v):
		return isinstance(v, str);
	def py_2or3_unicode_upcast(value):
		return str(value);
	def py_2or3_unicode_obj(obj):
		return str(obj);
else:
	# Version 2
	def py_2or3_byte_to_int(value):
		return ord(value);
	def py_2or3_int_to_byte(value):
		return chr(value);
	def py_2or3_intlist_to_bytes(value):
		return b"".join([ chr(i) for i in value ]);
	def py_2or3_byte_ord(char):
		return ord(char);
	def py_2or3_var_is_bytes(value):
		return isinstance(value, str);
	def py_2or3_var_is_unicode(value):
		return isinstance(value, unicode);
	def py_2or3_var_is_integer(v):
		return isinstance(v, ( int , long ));
	def py_2or3_var_is_string(v):
		return isinstance(v, basestring);
	def py_2or3_unicode_upcast(value):
		if (isinstance(value, str)):
			return value.decode(u"latin");
		return unicode(value);
	def py_2or3_unicode_obj(obj):
		return unicode(obj);



# XML escaping
__re_xml_escaper = re.compile(r"[\"<>&]");
__re_xml_escaper_map = {
	u"\"": u"&quot;",
	u"<": u"&lt;",
	u">": u"&gt;",
	u"&": u"&amp;",
};

def xml_escape(value):
	return __re_xml_escaper.sub(lambda m: __re_xml_escaper_map[m.group(0)], value);



# Type constants
INT = 0;
UINT = 1;
FLOAT = 2;
STRING = 3;
UNICODE = 4;
DATE = 5;
CONTAINER = 6;
BINARY = 7;



# Error classes
class EBMLError(Exception):
	pass;

class SchemaError(EBMLError):
	NAME_ALREADY_USED = u"Tag name already being used in schema";
	ID_CLASS_INVALID = u"Id class is invalid";
	ID_LENGTH_INVALID = u"Id length is invalid";
	ID_LENGTH_INVALID_FOR_CLASS = u"Id length is invalid for its class";
	ID_RESERVED = u"Id is reserved";

class StreamError(EBMLError):
	STREAM_NOT_READABLE = u"The stream is not readable";
	STREAM_NOT_SEEKABLE = u"An error occured trying to seek in the stream";
	STREAM_NOT_SKIPPABLE = u"An error occured trying to skip part of the stream";

	def __init__(self, message, info, pos):
		self.message = message;
		self.info = info;
		self.pos = pos;

	def __str__(self):
		s = self.message;
		if (self.info is not None):
			s += u"; {0:s}".format(self.info);
		if (self.pos is not None):
			s += u"; (@{0:d})".format(self.pos);
		return s;

class DecodeError(EBMLError):
	UNEXPECTED_EOS = u"Unexpected end of stream";
	ID_CLASS_INVALID = u"Id class is invalid";
	ID_LENGTH_INVALID = u"Id length is invalid";
	ID_RESERVED = u"Id is reserved";
	SIZE_CLASS_INVALID = u"Size class is invalid";
	SIZE_RESERVED = u"Size is reserved";
	DATA_LENGTH_INCORRECT = u"Data length incorrect";
	DATA_LENGTH_MISMATCH = u"Data length mismatch";
	DATA_LENGTH_OVERFLOW = u"Data length overflows container size";
	STRING_INVALID = u"Improperly formatted string";
	UTF8_INVALID = u"Improperly formatted unicode";
	FLOAT_LENGTH_INVALID = u"Invalid length for a floating point number";
	DATE_LENGTH_INVALID = u"Invalid length for a date";

	SCHEMA_ID_NOT_FOUND = u"Id not found in schema";
	SCHEMA_ID_NOT_FOUND_WITH_CORRECT_LEVEL = u"Id not found in schema with correct level";
	SCHEMA_VERSION_INVALID = u"Invalid schema version for element";
	SCHEMA_VALIDATION_FAILED = u"Schema validator function returned false";

	def __init__(self, message, info, pos):
		self.message = message;
		self.info = info;
		self.pos = pos;

	def __str__(self):
		s = self.message;
		if (self.info is not None):
			s += u"; {0:s}".format(self.info);
		if (self.pos is not None):
			s += u"; (@{0:d})".format(self.pos);
		return s;

class EncodeError(EBMLError):
	SIZE_NEGATIVE = u"Size cannot be negative";
	SIZE_CLASS_INVALID = u"Size class is invalid";
	SIZE_TOO_LARGE = u"Size too high to be encoded";

class ElementError(EBMLError):
	IMPLEMENTATION_ERROR = u"Method not implemented";
	VALUE_ERROR = u"Error setting an element's value";
	SCHEMA_VALIDATION_FAILED = u"Schema validator function returned false";

	FLOAT_PRECISION_INVALID = u"Invalid floating point precision";

	DESCRIPTOR_NOT_FOUND = u"Descriptor could not be found in schema";

	INSERT_RELATIVE_INVALID = u"Relative for insertion is invalid";

	SIZE_TOO_LARGE = u"Size too high to be encoded";

	PARENT_INCORRECT = u"Element is not the parent element's child";

	LEVEL_ERROR = u"Child could not be added to parent becuase the level is not valid in the schema";

	RECURSIVE_CHILD = u"An element may not contain itself";
	
	CANNOT_TURN_OBJECT_INTO_POINTER = u"An element that was not read from a stream cannot be converted to a pointer";

class SelectorError(EBMLError):
	PSEUDO_SELECTOR_INVALID = u"Pseudo selector invalid";
	PSEUDO_SELECTOR_EXTRA_PAREN = u"Pseudo selector parenthesized when it shouldn't be";
	PSEUDO_SELECTOR_MISSING_PAREN = u"Pseudo selector missing parentheses";
	PSEUDO_SELECTOR_MISSING_PAREN_END = u"Pseudo selector missing closing parenthesis";

	NOT_SELECTOR_INVALID = u":not selector invalid";

	BRACKETED_MISSING_END = u"Bracketed expression missing ending bracket";

	NO_SELECTOR_BEFORE_RELATIONSHIP = u"No selector was found preceeding a relationship operator";
	NO_SELECTOR_AFTER_RELATIONSHIP = u"No selector was found following a relationship operator";

	END_OF_SELECTOR_NOT_REACHED = u"Characters found after parsing was completed";

	TAG_NAME_SELECTOR_NOT_FIRST = u"Selector name did not appear first";

	STRING_EXPRESSION_INVALID = u"String expression invalid";
	STRING_EXPRESSION_NOT_CLOSED = u"String expression not closed";

	NTH_EXPRESSION_INVALID = u"No valid nth expression was found";



# Context classes
class ReadContext(object):
	def __init__(self, schema, stream):
		self.schema = schema;
		self.stream = stream;
		self.warnings = [];

		try:
			self.pos = self.stream.tell();
		except ValueError as e:
			raise StreamError(StreamError.STREAM_NOT_READABLE, py_2or3_unicode_obj(e), 0);

		self.pos_limit = -1;
		self.pos_limit_stack = [ self.pos_limit ];

		self.decode_depth = -1;

	def warn(self, level, message, info):
		if (level == Schema.STRICT):
			raise DecodeError(message, info, self.pos);
		elif (level == Schema.WARN):
			self.warnings.append(( message , info , self.pos ));
	def warn_data_length(self, expected, found):
		self.warn(self.schema.strict_data_length, DecodeError.DATA_LENGTH_INCORRECT, u"Expected {0:d}; found {1:d}".format(expected, found));

	def read(self, length):
		# Length limit
		if (self.pos_limit >= 0 and self.pos + length > self.pos_limit):
			length = self.pos_limit - self.pos;

		# Read
		try:
			d = self.stream.read(length);
		except ValueError as e:
			raise StreamError(StreamError.STREAM_NOT_READABLE, py_2or3_unicode_obj(e), 0);
		self.pos += len(d);
		return d;
	def skip(self, length):
		# Length limit
		if (self.pos_limit >= 0 and self.pos + length > self.pos_limit):
			length = self.pos_limit - self.pos;

		# Skip
		try:
			self.stream.seek(length, 1);
		except ValueError:
			# Non-seekable?
			try:
				d = self.stream.read(length);
				length = len(d);
			except ValueError as e:
				# Stream is invalid
				raise StreamError(StreamError.STREAM_NOT_SKIPPABLE, py_2or3_unicode_obj(e), pos);

		# Done
		self.pos += length;
		return length;
	def seek(self, pos):
		try:
			self.stream.seek(pos, 0);
		except ValueError as e:
			raise StreamError(StreamError.STREAM_NOT_SEEKABLE, py_2or3_unicode_obj(e), pos);

		self.pos = pos;
		return True;

	def read_id(self):
		# Read byte
		b = self.read(1);
		if (len(b) < 1):
			return None;
		id = b;
		b = py_2or3_byte_ord(id[0]);

		# Class
		found = False;
		for count in range(4): # 4 bits
			if ((b & (0x80 >> count)) != 0):
				found = True;
				break;

		# Invalid
		if (not found):
			raise DecodeError(DecodeError.ID_CLASS_INVALID, u"[{0:s}]".format(ElementDescriptor.id_binary_to_str(id)), self.pos);

		# Form id
		all_bits_one = ((b | ((0xFF00 >> count) & 0xFF)) == 0xFF);
		if (count > 0):
			# Read
			data = self.read(count);
			if (len(data) < count):
				raise DecodeError(DecodeError.UNEXPECTED_EOS, None, self.pos);

			for i in range(count):
				# Decode
				b = py_2or3_byte_ord(data[i]);

				if (all_bits_one and b != 0xFF):
					all_bits_one = False;

			id += data;

		# Invalid
		if (all_bits_one):
			raise DecodeError(DecodeError.ID_RESERVED, None, self.pos);

		# Done
		return id;
	def read_size(self):
		# Read byte
		b = self.read(1);
		if (len(b) < 1):
			raise DecodeError(DecodeError.UNEXPECTED_EOS, None, self.pos);
		b = py_2or3_byte_ord(b[0]);

		# Class
		found = False;
		for count in range(8): # 8 bits
			if ((b & (0x80 >> count)) != 0):
				found = True;
				break;

		# Valid
		if (not found):
			raise DecodeError(DecodeError.SIZE_CLASS_INVALID, None, self.pos);

		# Form size
		mask = (~(0xFF00 >> (count + 1)) & 0xFF);
		size = b & mask;
		all_bits_one = (size == mask);
		if (count > 0):
			# Read
			data = self.read(count);
			if (len(data) < count):
				raise DecodeError(DecodeError.UNEXPECTED_EOS, None, self.pos);

			for i in range(count):
				# Decode
				b = py_2or3_byte_ord(data[i]);

				# Update
				size <<= 8;
				size += b;

				# All ones
				if (all_bits_one and b != 0xFF):
					all_bits_one = False;

		# Invalid
		if (all_bits_one):
			raise DecodeError(DecodeError.SIZE_RESERVED, None, self.pos);

		# Done
		return ( size , count );

	def push_limit(self, size):
		p_next = self.pos + size;

		if (self.pos_limit >= 0 and p_next > self.pos_limit):
			# Size greater than it should be
			self.warn(
				self.schema.strict_data_length,
				DecodeError.DATA_LENGTH_OVERFLOW,
				u"Size overflows container's size by {0:d} bytes".format(p_next - self.pos_limit)
			);
			p_next = self.pos_limit;

		self.pos_limit_stack.append(p_next);
		self.pos_limit = p_next;
	def pop_limit(self):
		limit_pre = self.pos_limit_stack.pop();
		self.pos_limit = self.pos_limit_stack[-1];

		if (self.pos != limit_pre):
			# Size unexpected
			self.warn(
				self.schema.strict_data_length,
				DecodeError.DATA_LENGTH_MISMATCH,
				u"Expected to be at position {0:d}; actually at position {1:d}".format(limit_pre, self.pos)
			);

class WriteContext(object):
	@classmethod
	def encode_size(cls, value, desired_class=0):
		# Validate
		if (desired_class < 0 or desired_class >= 8):
			raise EncodeError(EncodeError.SIZE_CLASS_INVALID);
		if (value < 0):
			raise EncodeError(EncodeError.SIZE_NEGATIVE);
		if (value > (2 ** (7 * (desired_class + 1))) - 2):
			raise EncodeError(EncodeError.SIZE_TOO_LARGE);

		# Encode
		b = [];
		desired_class += 1;
		for i in range(desired_class):
			b.append(value & 0xFF);
			value >>= 8;

		# Add class
		b[-1] |= (0x100) >> desired_class;
		return py_2or3_intlist_to_bytes(reversed(b));

	def __init__(self, stream, pointers_temporary=True):
		self.stream = stream;
		self.stream_seekable = True;

		self.pointers_temporary = pointers_temporary;

	def write(self, data):
		self.stream.write(data);



# Schema classes
class Schema(object):
	STRICT = 2;
	WARN = 1;
	IGNORE = 0;

	def __init__(self):
		self.version = 0;
		self.pointers_enabled = True;
		self.tags = {};
		self.names = {};

		self.strict_unicode = self.STRICT;
		self.strict_string = self.STRICT;
		self.strict_missing_id = self.WARN;
		self.strict_version_check = self.WARN;
		self.strict_data_length = self.STRICT;
		self.strict_validator = self.STRICT;

	def define(self, id, name, el_type, level=u"g", versions=0, validator=None, pointer=False):
		# Fix arguments and validate
		if (isinstance(id, tuple) or isinstance(id, list)):
			id = ElementDescriptor.id_list_to_binary(id);
		elif (not py_2or3_var_is_bytes(id)):
			id = ElementDescriptor.id_str_to_binary(id);

		ElementDescriptor.id_binary_validate(id);


		if (name is None):
			name = ElementDescriptor.id_binary_to_name(id);

		if (name in self.names):
			raise SchemaError(SchemaError.NAME_ALREADY_USED);


		# Create
		d = ElementDescriptor(id, name, el_type, level, versions, validator, pointer, 0);

		# Add
		self.names[name] = d;
		if (d.id in self.tags):
			self.tags[d.id].append(d);
		else:
			self.tags[d.id] = [ d ];

		# Done
		return d;

	def element(self, id, value=None):
		# Find descriptor
		if (py_2or3_var_is_string(id)):
			# String name
			if (id in self.names):
				descriptor = self.names[id];
		else:
			# Id is a descriptor
			if (id.name in self.names and id is self.names[id.name]):
				# Create node
				descriptor = id;
			else:
				# Error
				raise ElementError(ElementError.DESCRIPTOR_NOT_FOUND);

		# Create
		el = ElementClasses[descriptor.type](None, descriptor, None, 0, 0, 0, 0, True);

		# Value
		if (value is not None):
			el.set(value);

		# Done
		return el;

	def root(self):
		descriptor = ElementDescriptor(b"", u"", BINARY, -1, 0, None, False, ElementDescriptor.ROOT);
		return ElementContainer(None, descriptor, None, -1, 0, 0, 0, True);

class ElementDescriptor(object):
	MISSING = 0x1;
	ROOT = 0x2;

	def __init__(self, id, name, el_type, level, versions, validator, pointer, flags):
		# Level
		if (py_2or3_var_is_integer(level)):
			self.level = level;
			self.level_recursive = False;
			self.level_global =  False;
		elif (level == u"g"):
			self.level = 0;
			self.level_recursive = True;
			self.level_global =  True;
		elif (level[-1] == u"+"):
			self.level = int(level[: -1], 10);
			self.level_recursive = True;
			self.level_global =  False;
		else:
			self.level = int(level, 10);
			self.level_recursive = False;
			self.level_global =  False;

		# Other vars
		self.id = id;
		self.name = name;
		self.type = el_type;
		self.versions = versions;
		self.validator = validator;
		self.pointer = pointer;
		self.flags = flags;

	@classmethod
	def id_str_to_binary(cls, id):
		return py_2or3_intlist_to_bytes([ int(id[i : i + 2], 16) for i in range(0, len(id), 2) ]);

	@classmethod
	def id_list_to_binary(cls, id):
		return py_2or3_intlist_to_bytes(id);

	@classmethod
	def id_binary_to_str(cls, id):
		return u"".join([ u"{0:02X}".format(py_2or3_byte_to_int(c)) for c in id]);

	@classmethod
	def id_binary_to_name(cls, id):
		return u"0x{0:s}".format(u"".join([ u"{0:0X}".format(py_2or3_byte_to_int(c)) for c in id ]));

	@classmethod
	def id_binary_validate(cls, id):
		# Length check
		id_len = len(id);
		if (id_len == 0 or id_len > 4):
			raise SchemaError.ID_LENGTH_INVALID;

		# Class
		b = py_2or3_byte_to_int(id[0]);
		found = False;
		for count in range(4): # 4 bits
			if ((b & (0x80 >> count)) != 0):
				found = True;
				break;

		# Invalid
		if (not found):
			raise SchemaError.ID_CLASS_INVALID;

		# Invalid length
		if (id_len != count + 1):
			raise SchemaError.ID_LENGTH_INVALID_FOR_CLASS;

		# Check for all 1's
		all_bits_one = ((b | ((0xFF00 >> count) & 0xFF)) == 0xFF);
		for i in range(1, id_len):
			if (all_bits_one and py_2or3_byte_to_int(id[i]) != 0xFF):
				all_bits_one = False;

		# Done
		if (all_bits_one):
			raise SchemaError.ID_RESERVED;



# Element classes
class Element(object):
	def __init__(self, context, descriptor, parent, level, pos, size, size_class):
		self.parent = parent;
		self.next_sibling = None;
		self.previous_sibling = None;
		self.level = level;
		self.child_id = 0;
		self.child_of_type_id = 0;

		self.descriptor = descriptor;
		if (self.descriptor.level_global):
			self.descriptor_level = level;
		else:
			self.descriptor_level = self.descriptor.level;
		self.context = context;
		self.value = None;

		self.size = size;
		self.size_class = size_class;
		self.stream_pos = pos;
		self.stream_size = size;
		self.stream_size_class = size_class;

	def __repr__(self):
		return u"{0:s}()".format(self.__class__.__name__);

	def get(self, decode_depth=-1):
		if (self.value is None):
			# Seek
			self.context.seek(self.stream_pos);
			self._decode(decode_depth);

		# Done
		return self.value;

	def set(self, value):
		# Set
		self._set_value(value);

		# Validate
		if (self.descriptor.validator is not None and not self.descriptor.validator(value)):
			raise ElementError(ElementError.SCHEMA_VALIDATION_FAILED);

	def is_pointer(self):
		return (self.value is None);

	def to_pointer(self):
		# Can't convert
		if (self.context is None):
			raise ElementError(ElementError.CANNOT_TURN_OBJECT_INTO_POINTER);
	
		# Clear value
		self.value = None;

		# Revert size
		self._set_size_and_class(self.stream_size, self.stream_size_class);

	def clear(self):
		raise ElementError(ElementError.IMPLEMENTATION_ERROR);

	def to_xml(self):
		indent = 0;
		indent_str = u"\t";

		# Pointer
		if (self.is_pointer()):
			# Pointer
			data = self._to_xml_pointer(indent, indent_str);
		else:
			# Data
			data = self._to_xml_list(indent, indent_str);

		# Join
		return u"".join(data);

	def get_tag_name(self):
		return self.descriptor.name;

	def value_string_matches(self, value_str):
		return False;

	def insert(self, element, before=None, after=None, prepend=False):
		raise ElementError(ElementError.IMPLEMENTATION_ERROR);

	def remove_child(self, element):
		raise ElementError(ElementError.IMPLEMENTATION_ERROR);

	def remove(self):
		if (self.parent is not None):
			self.parent.remove_child(self);

	def is_child(self, element):
		return False;

	def get_full_size(self):
		return len(self.descriptor.id) + self.size_class + 1 + self.size;

	def _to_xml_list(self, indent, indent_str):
		raise ElementError(ElementError.IMPLEMENTATION_ERROR);

	def _to_xml_pointer(self, indent, indent_str):
		# Form tag
		return [ u"{0:s}<{1:s} type=\"{2:s}\" pointer=\"true\" pos=\"{3:s}\" size=\"{4:s}\" />\n".format(
			indent_str * indent,
			xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
			xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
			xml_escape(py_2or3_unicode_upcast(self.stream_pos)),
			xml_escape(py_2or3_unicode_upcast(self.stream_size))
		) ];

	def _decode(self, decode_depth=-1):
		# Limit
		self.context.push_limit(self.stream_size);

		# Update decoding depth
		if (decode_depth >= 0):
			dd_pre = self.context.decode_depth;
			self.context.decode_depth = decode_depth;

		# Read and decode
		value = self._decode_value();

		# Validate
		if (self.descriptor.validator is not None and not self.descriptor.validator(value)):
			self.context.warn(
				self.context.schema.strict_validator,
				DecodeError.SCHEMA_VALIDATION_FAILED,
				u"{0:s} [{1:s}]".format(self.descriptor.name, ElementDescriptor.id_binary_to_name(self.descriptor.id))
			);

		# Restore decoding depth
		if (decode_depth >= 0):
			self.context.decode_depth = dd_pre;

		# Pop limit
		self.context.pop_limit();

		# Done
		self.value = value;

	def _decode_value(self):
		raise ElementError(ElementError.IMPLEMENTATION_ERROR);

	def _encode(self, context):
		# Pointer
		nullify = False;
		if (self.value is None):
			# Seek
			if (context.pointers_temporary):
				nullify = True;
			self.context.seek(self.stream_pos);
			self._decode(0);

		# Write
		context.write(self.descriptor.id);
		context.write(WriteContext.encode_size(self.size, self.size_class));
		self._encode_value(context);

		# Nullify again?
		if (nullify == True):
			self.value = None;

	def _encode_value(self, context):
		raise ElementError(ElementError.IMPLEMENTATION_ERROR);

	def _set_value(self, value):
		raise ElementError(ElementError.IMPLEMENTATION_ERROR);

	def _set_size(self, size):
		if (self.size == size): return;

		size_class = self.__get_size_class(size);
		diff = (size - self.size) + (size_class - self.size_class);

		self.size = size;
		self.size_class = size_class;

		n = self.parent;
		while (n is not None):
			n.size += diff;
			n = n.parent;

	def _set_size_and_class(self, size, size_class):
		if (self.size == size and self.size_class == size_class): return;

		diff = (size - self.size) + (size_class - self.size_class);

		self.size = size;
		self.size_class = size_class;

		n = self.parent;
		while (n is not None):
			n.size += diff;
			n = n.parent;

	def __get_size_class(self, value):
		# Get correct class
		#desired_class = int(math.log(value + 2, 128)); # Not precise enough
		desired_class = 0;
		while (value > (2 ** (7 * (desired_class + 1))) - 2):
			desired_class += 1;
			if (desired_class >= 8):
				raise ElementError(ElementError.SIZE_TOO_LARGE);

		return desired_class;

class ElementInt(Element):
	TYPE = INT;
	TYPE_STR = u"int";

	@classmethod
	def binary_to_value(cls, data):
		# Process
		if (len(data) > 0):
			v = py_2or3_byte_ord(data[0]);
			value = v;
			for i in range(1, len(data)):
				value = (value << 8) | py_2or3_byte_ord(data[i]);

			# Negative?
			if ((v & 0x80) != 0):
				value -= (0x1 << (len(data) * 8));

			# Done
			return value;
		else:
			# Assume 0
			return 0;



	def __init__(self, context, descriptor, parent, level, pos, size, size_class, construct=False):
		Element.__init__(self, context, descriptor, parent, level, pos, size, size_class);
		if (construct == True):
			self.value = 0;
			self.size = 1;

	def __repr__(self):
		if (self.is_pointer()):
			v = u"pointer";
		else:
			v = py_2or3_unicode_obj(self.value);
		return u"{0:s}({1:s})".format(self.__class__.__name__, v);

	def clear(self):
		self.set(0);

	def value_string_matches(self, value_str):
		try:
			v = int(value_str, 10);
		except ValueError:
			return False;

		return v == self.value;

	def _decode_value(self):
		# Read
		data = self.context.read(self.size);
		if (len(data) != self.size):
			self.context.warn_data_length(self.size, len(data));

		# Process
		return self.binary_to_value(data);

	def _encode_value(self, context):
		v = self.value;
		array = [];

		# Form array
		for i in range(self.size):
			array.append(v & 0xFF);
			v >>= 8;

		# Write
		context.write(py_2or3_intlist_to_bytes(reversed(array)));

	def _set_value(self, value):
		if (not py_2or3_var_is_integer(value)):
			raise ElementError(ElementError.VALUE_ERROR);

		size = self.__get_size_required(value);

		self.value = value;
		self._set_size(size);

	def _to_xml_list(self, indent, indent_str):
		# Form tag
		return [ u"{0:s}<{1:s} type=\"{2:s}\" value=\"{3:s}\" />\n".format(
			indent_str * indent,
			xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
			xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
			xml_escape(py_2or3_unicode_upcast(self.value))
		) ];

	def __get_size_required(self, value):
		if (value < 0):
			v = -value;
		else:
			v = value + 1;

		if (v <= 0x80):
			size = 1;
		else:
			size = 2 + int(math.log(int(v / 0x80), 256));

		return size;

class ElementUInt(Element):
	TYPE = UINT;
	TYPE_STR = u"uint";



	def __init__(self, context, descriptor, parent, level, pos, size, size_class, construct=False):
		Element.__init__(self, context, descriptor, parent, level, pos, size, size_class);
		if (construct == True):
			self.value = 0;
			self.size = 1;

	def __repr__(self):
		if (self.is_pointer()):
			v = u"pointer";
		else:
			v = py_2or3_unicode_obj(self.value);
		return u"{0:s}({1:s})".format(self.__class__.__name__, v);

	def clear(self):
		self.set(0);

	def value_string_matches(self, value_str):
		try:
			v = int(value_str, 10);
		except ValueError:
			return False;

		return v == self.value;

	def _decode_value(self):
		# Read
		data = self.context.read(self.size);
		if (len(data) != self.size):
			self.context.warn_data_length(self.size, len(data));

		# Process
		value = 0;
		for c in data:
			value = (value << 8) | py_2or3_byte_ord(c);

		# Done
		return value;

	def _encode_value(self, context):
		v = self.value;
		array = [];

		# Form array
		for i in range(self.size):
			array.append(v & 0xFF);
			v >>= 8;

		# Write
		context.write(py_2or3_intlist_to_bytes(reversed(array)));

	def _set_value(self, value):
		if (not py_2or3_var_is_integer(value) or value < 0):
			raise ElementError(ElementError.VALUE_ERROR);

		if (value < 256):
			size = 1;
		else:
			size = 1 + int(math.log(value, 256));

		self.value = value;
		self._set_size(size);

	def _to_xml_list(self, indent, indent_str):
		# Form tag
		return [ u"{0:s}<{1:s} type=\"{2:s}\" value=\"{3:s}\" />\n".format(
			indent_str * indent,
			xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
			xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
			xml_escape(py_2or3_unicode_upcast(self.value))
		) ];

class ElementFloat(Element):
	TYPE = FLOAT;
	TYPE_STR = u"float";

	FLOAT_PRECISION = 4;
	DOUBLE_PRECISION = 8;



	def __init__(self, context, descriptor, parent, level, pos, size, size_class, construct=False):
		Element.__init__(self, context, descriptor, parent, level, pos, size, size_class);
		if (construct == True):
			self.value = 0.0;
			self.size = self.DOUBLE_PRECISION;

	def __repr__(self):
		if (self.is_pointer()):
			v = u"pointer";
		else:
			v = py_2or3_unicode_obj(self.value);
		return u"{0:s}({1:s})".format(self.__class__.__name__, v);

	def clear(self):
		self.set(0.0);

	def value_string_matches(self, value_str):
		try:
			v = float(value_str);
		except ValueError:
			return False;

		return v == self.value;

	def set_precision(self, precision):
		if (precision != self.FLOAT_PRECISION and precision != self.DOUBLE_PRECISION):
			raise ElementError(ElementError.FLOAT_PRECISION_INVALID);

		self._set_size(precision);

	def _decode_value(self):
		# Read
		data = self.context.read(self.size);
		if (len(data) != self.size):
			self.context.warn_data_length(self.size, len(data));

		# Done
		if (self.size == self.FLOAT_PRECISION):
			return struct.unpack(u">f", data)[0];
		elif (self.size == self.DOUBLE_PRECISION):
			return struct.unpack(u">d", data)[0];
		else:
			# Invalid
			raise EMBL.Exception(
				EMBL.Exception.FLOAT_LENGTH_INVALID,
				u"Expected a float of size {0:d} or {1:d}, not {2:d}".format(self.FLOAT_PRECISION, self.DOUBLE_PRECISION, self.size),
				self.pos
			);

	def _encode_value(self, context):
		if (self.size == self.FLOAT_PRECISION):
			# Write
			context.write(struct.pack(u">f", self.value));
		elif (self.size == self.DOUBLE_PRECISION):
			# Write
			context.write(struct.pack(u">d", self.value));
		else:
			context.write(b"\x00" * self.size);

	def _set_value(self, value):
		self.value = value;

	def _to_xml_list(self, indent, indent_str):
		# Form tag
		return [ u"{0:s}<{1:s} type=\"{2:s}\" value=\"{3:s}\" />\n".format(
			indent_str * indent,
			xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
			xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
			xml_escape(py_2or3_unicode_upcast(self.value))
		) ];

class ElementString(Element):
	TYPE = STRING;
	TYPE_STR = u"string";

	__re_string_ascii_replacer = re.compile(r"[^\x20-\x7F]+");



	def __init__(self, context, descriptor, parent, level, pos, size, size_class, construct=False):
		Element.__init__(self, context, descriptor, parent, level, pos, size, size_class);
		if (construct == True):
			self.value = u"";
			self.size = 0;

	def __repr__(self):
		if (self.is_pointer()):
			v = u"pointer";
		else:
			v = self.value;
			if (len(v) > 16):
				v = v[0 : 16];
				v = repr(v) + u"...";
			else:
				v = repr(v);
		return u"{0:s}({1:s})".format(self.__class__.__name__, v);

	def clear(self):
		self.set(u"");

	def value_string_matches(self, value_str):
		return value_str == self.value;

	def _decode_value(self):
		# Read
		data = self.context.read(self.size);
		if (len(data) != self.size):
			self.context.warn_data_length(self.size, len(data));

		# Replace more chars
		value = self.__re_string_ascii_replacer.sub(u"", data.decode(u"latin", u"ignore"));
		if (len(value) != len(data)):
			self.context.warn(
				self.context.schema.strict_string,
				DecodeError.STRING_INVALID,
				u"Raw length={0:d}, decoded length={1:d})".format(len(data), len(value)),
			);

		# Done
		return value;

	def _encode_value(self, context):
		context.write(self.value.encode(u"latin", u"ignore"));

	def _set_value(self, value):
		if (py_2or3_var_is_bytes(value)):
			# Convert
			value2 = self.__re_string_ascii_replacer.sub(u"", value.decode(u"latin", u"ignore"));
			if (len(value2) != len(value)):
				raise ElementError(ElementError.VALUE_ERROR);

			# Set
			self.value = value2;
			self._set_size(len(self.value));
		elif (py_2or3_var_is_unicode(value)):
			# Convert
			value2 = self.__re_string_ascii_replacer.sub(u"", value);
			if (len(value2) != len(value)):
				raise ElementError(ElementError.VALUE_ERROR);

			# Set
			self.value = value2;
			self._set_size(len(self.value));
		else:
			# Invalid type
			raise ElementError(ElementError.VALUE_ERROR);

	def _to_xml_list(self, indent, indent_str):
		# Form tag
		return [ u"{0:s}<{1:s} type=\"{2:s}\" value=\"{3:s}\" />\n".format(
			indent_str * indent,
			xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
			xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
			xml_escape(py_2or3_unicode_upcast(self.value))
		) ];

class ElementUnicode(Element):
	TYPE = UNICODE;
	TYPE_STR = u"unicode";



	def __init__(self, context, descriptor, parent, level, pos, size, size_class, construct=False):
		Element.__init__(self, context, descriptor, parent, level, pos, size, size_class);
		if (construct == True):
			self.value = u"";
			self.size = 0;

	def __repr__(self):
		if (self.is_pointer()):
			v = u"pointer";
		else:
			v = self.value;
			if (len(v) > 16):
				v = v[0 : 16];
				v = repr(v) + "...";
			else:
				v = repr(v);
		return u"{0:s}({1:s})".format(self.__class__.__name__, v);

	def clear(self):
		self.set(u"");

	def value_string_matches(self, value_str):
		return value_str == self.value;

	def _decode_value(self):
		# Read
		data = self.context.read(self.size);
		if (len(data) != self.size):
			self.context.warn_data_length(self.size, len(data));

		# Process
		try:
			value = data.decode(u"utf-8", u"strict");
		except UnicodeDecodeError:
			self.context.warn(
				self.context.schema.strict_unicode,
				DecodeError.UTF8_INVALID,
				None
			);
			value = data.decode(u"utf-8", u"ignore");

		# Done
		return value;

	def _encode_value(self, context):
		context.write(self.value.encode(u"utf-8", u"strict"));

	def _set_value(self, value):
		if (py_2or3_var_is_bytes(value)):
			# Convert
			size = len(value);
			try:
				value = value.decode(u"latin", u"strict");
			except UnicodeDecodeError:
				raise ElementError(ElementError.VALUE_ERROR);

			# Set
			self.value = value;
			self._set_size(size);
		elif (py_2or3_var_is_unicode(value)):
			# Size
			try:
				size = len(value.encode(u"utf-8", u"strict"));
			except UnicodeEncodeError:
				raise ElementError(ElementError.VALUE_ERROR);

			# Set
			self.value = value;
			self._set_size(size);
		else:
			# Invalid type
			raise ElementError(ElementError.VALUE_ERROR);

	def _to_xml_list(self, indent, indent_str):
		# Form tag
		return [ u"{0:s}<{1:s} type=\"{2:s}\" value=\"{3:s}\" />\n".format(
			indent_str * indent,
			xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
			xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
			xml_escape(py_2or3_unicode_upcast(self.value))
		) ];

class ElementDate(Element):
	TYPE = DATE;
	TYPE_STR = u"date";

	class Date(object):
		class UTCTimezone(datetime.tzinfo):
			def __init__(self):
				self.offset = datetime.timedelta(0);
			def utcoffset(self, dt):
				return self.offset;
			def tzname(self, dt):
				return u"UTC";
			def dst(self, dt):
				return self.offset;

		__date_timezone = UTCTimezone();
		__date_offset_base = datetime.datetime(2001, 1, 1, 0, 0, 0, 0, __date_timezone);
		__date_offset = __date_offset_base - datetime.datetime.fromtimestamp(0, __date_timezone);
		__date_offset = (__date_offset.seconds + __date_offset.days * 24 * 60 * 60);

		def __init__(self, year, month, day, hour=0, minute=0, second=0, nanoseconds=0):
			self.year = year;
			self.month = month;
			self.day = day;
			self.hour = hour;
			self.minute = minute;
			self.second = second;
			self.nanoseconds = nanoseconds;

		@classmethod
		def from_timestamp(cls, value):
			# Convert to date
			nanoseconds = value % (10 ** 9);
			seconds = int(value / (10 ** 9));
			d = datetime.datetime.fromtimestamp(cls.__date_offset + seconds, cls.__date_timezone);

			# Done
			return cls(d.year, d.month, d.day, d.hour, d.minute, d.second, nanoseconds);

		def to_timestamp(self):
			diff = datetime.datetime(self.year, self.month, self.day, self.hour, self.minute, self.second, 0, self.__date_timezone) - self.__date_offset_base;
			diff_seconds = (diff.seconds + diff.days * 24 * 60 * 60);
			return diff_seconds * (10 ** 9) + self.nanoseconds;

		def to_string(self):
			return u"{0:04d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6:09d}Z".format(self.year, self.month, self.day, self.hour, self.minute, self.second, self.nanoseconds);



	def __init__(self, context, descriptor, parent, level, pos, size, size_class, construct=False):
		Element.__init__(self, context, descriptor, parent, level, pos, size, size_class);
		if (construct == True):
			self.value = self.Date.from_timestamp(0);
			self.size = 8;

	def __repr__(self):
		if (self.is_pointer()):
			v = u"pointer";
		else:
			v = repr(self.value.to_string());
		return u"{0:s}({1:s})".format(self.__class__.__name__, v);

	def clear(self):
		self.set(0);

	def value_string_matches(self, value_str):
		return value_str == self.value.to_string();

	def _decode_value(self):
		# Validate
		if (self.size < 8):
			raise EMBL.Exception(EMBL.Exception.DATE_LENGTH_INVALID, u"Expected a date length of at least 8, not {0:d}".format(self.size), self.pos);

		# Read
		data = self.context.read(self.size);
		if (len(data) != self.size):
			self.context.warn_data_length(self.size, len(data));

		# Process
		value = ElementInt.binary_to_value(data);

		# Done
		return self.Date.from_timestamp(value);

	def _encode_value(self, context):
		# Convert date to int
		v = self.value.to_timestamp();

		# Convert to byte representation
		array = [];
		for i in range(self.size):
			array.append(v & 0xFF);
			v >>= 8;

		# Write
		context.write(py_2or3_intlist_to_bytes(reversed(array)));

	def _set_value(self, value):
		if (isinstance(value, ( list , tuple ))):
			# Time array
			self.value = self.Date(*value);
		elif (isinstance(value, self.Date)):
			# Date
			self.value = value;
		else: # Assume integer
			self.value = self.Date.from_timestamp(value);

	def _to_xml_list(self, indent, indent_str):
		# Form tag
		return [ u"{0:s}<{1:s} type=\"{2:s}\" value=\"{3:s}\" />\n".format(
			indent_str * indent,
			xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
			xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
			xml_escape(py_2or3_unicode_upcast(self.value.to_string()))
		) ];

class ElementBinary(Element):
	TYPE = BINARY;
	TYPE_STR = u"binary";



	def __init__(self, context, descriptor, parent, level, pos, size, size_class, construct=False):
		Element.__init__(self, context, descriptor, parent, level, pos, size, size_class);
		if (construct == True):
			self.value = b"";
			self.size = 0;

	def __repr__(self):
		if (self.is_pointer()):
			v = u"pointer";
		else:
			v = self.value;
			ext = u"";

			if (len(v) > 16):
				v = v[0:16];
				ext = u"...";

			v = repr(u"".join([ u"{0:02X}".format(py_2or3_byte_ord(c)) for c in v ])) + ext;

		return u"{0:s}({1:s})".format(self.__class__.__name__, v);

	def clear(self):
		self.set(b"");

	def value_string_matches(self, value_str):
		if (len(value_str) != len(self.value) * 2):
			return False;

		for i in range(0, len(value_str), 2):
			if (int(value_str[i : i + 2], 16) != py_2or3_byte_ord(self.value[i])):
				return False;

		return True;

	def _decode_value(self):
		# Read
		data = self.context.read(self.size);
		if (len(data) != self.size):
			self.context.warn_data_length(self.size, len(data));

		# Done
		return data;

	def _encode_value(self, context):
		context.write(self.value);

	def _set_value(self, value):
		if (py_2or3_var_is_bytes(value)):
			# Set
			self.value = value;
			self._set_size(len(self.value));
		elif (py_2or3_var_is_unicode(value)):
			# Convert
			try:
				value = value.encode(u"utf-8", u"strict");
			except UnicodeEncodeError:
				raise ElementError(ElementError.VALUE_ERROR);

			# Set
			self.value = value;
			self._set_size(len(self.value));
		else:
			# Invalid type
			raise ElementError(ElementError.VALUE_ERROR);

	def _to_xml_list(self, indent, indent_str):
		# Form tag
		if (len(self.value) > 16):
			return [ u"{0:s}<{1:s} type=\"{2:s}\" value-length=\"{3:s}\" />\n".format(
				indent_str * indent,
				xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
				xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
				xml_escape(py_2or3_unicode_upcast(len(self.value)))
			) ];
		else:
			return [ u"{0:s}<{1:s} type=\"{2:s}\" value=\"{3:s}\" />\n".format(
				indent_str * indent,
				xml_escape(py_2or3_unicode_upcast(self.descriptor.name)),
				xml_escape(py_2or3_unicode_upcast(self.TYPE_STR)),
				xml_escape(u"".join([ u"{0:02X}".format(py_2or3_byte_ord(c)) for c in self.value ]))
			) ];

class ElementContainer(Element):
	TYPE = CONTAINER;
	TYPE_STR = u"container";

	# Element container
	class Container(object):
		def __init__(self):
			self.children = [];
			self.children_of_type = {};

		def insert_at_end(self, element):
			# Add
			element.child_id = len(self.children);
			self.children.append(element);

			# Type id
			type_name = element.descriptor.name;
			if (type_name in self.children_of_type):
				# Add to end of array
				array = self.children_of_type[type_name];
				element.child_of_type_id = len(array);
				array.append(element);
			else:
				# New array
				element.child_of_type_id = 0;
				self.children_of_type[type_name] = [ element ];

			# Link
			if (element.child_id > 0):
				element.previous_sibling = self.children[element.child_id - 1];

		def insert(self, element, position):
			# Update children list
			self.children.insert(position, element);
			for i in range(position, len(self.children)):
				self.children[i].child_id = i;

			# Link
			if (position > 0):
				e = self.children[position - 1];
				element.previous_sibling = e;
				e.next_sibling = element;
			if (position + 1 < len(self.children)):
				e = self.children[position + 1];
				element.next_sibling = e;
				e.previous_sibling = element;

			# Children of type
			type_name = element.descriptor.name;
			if (type_name in self.children_of_type):
				# Find position
				id = 0;
				array = self.children_of_type[type_name];
				for i in range(position):
					if (self.children[i].descriptor.name == type_name):
						id += 1;

				# Update array
				array.insert(id, element);
				for i in range(id, len(array)):
					array[i].child_id = i;
			else:
				# New array
				element.child_of_type_id = 0;
				self.children_of_type[type_name] = [ element ];

		def remove(self, element):
			# Remove from both lists
			self.children.pop(element.child_id);
			array = self.children_of_type[element.descriptor.name];
			array.pop(element.child_of_type_id);

			# Link
			if (element.previous_sibling is not None):
				element.previous_sibling.next_sibling = element.next_sibling;
			if (element.next_sibling is not None):
				element.next_sibling.previous_sibling = element.previous_sibling;

			# Update ids
			for i in range(element.child_id, len(self.children)):
				self.children[i].child_id = i;
			for i in range(element.child_of_type_id, len(array)):
				array[i].child_of_type_id = i;



	def __init__(self, context, descriptor, parent, level, pos, size, size_class, construct=False):
		Element.__init__(self, context, descriptor, parent, level, pos, size, size_class);
		if (construct == True):
			self.value = self.Container();
			self.size = 0;

	def __repr__(self):
		if (self.is_pointer()):
			v = u"pointer";
		else:
			cc = len(self.value.children);
			if (cc == 0):
				v = u"[No children]";
			elif (cc == 1):
				v = u"[1 child]";
			else:
				v = u"[{0:d} children]".format(len(self.value.children));

		return u"{0:s}({1:s})".format(self.__class__.__name__, v);

	def clear(self):
		# Pointer
		if (self.value is None):
			# Empty container
			self.value = self.Container();
			self._set_size(0);
			return;

		# De-parent children
		for c in self.value.children:
			self.__unparent(c);

		# Empty
		self.value.children = [];
		self.value.children_of_type = {};

		# Set size
		self._set_size(0);

	def insert(self, element, before=None, after=None, prepend=False):
		# Validate recursion
		if (element is self):
			raise ElementError(ElementError.RECURSIVE_CHILD);

		# Validate level
		d = element.descriptor;
		level_target = self.level + 1;
		if (not (level_target == d.level or (d.level_recursive and level_target >= d.level))):
			raise ElementError(ElementError.LEVEL_ERROR);

		# Insertion mode and validation
		insert_pos = None;
		if (before is not None):
			# Validate
			if (not self.is_child(before)):
				raise ElementError(ElementError.INSERT_RELATIVE_INVALID);

			# Insert
			insert_pos = before.child_id;
		elif (after is not None):
			# Validate
			if (not self.is_child(after)):
				raise ElementError(ElementError.INSERT_RELATIVE_INVALID);

			# Insert
			insert_pos = after.child_id + 1;
		elif (prepend):
			# Insert at beginning
			insert_pos = 0;


		# Pointer check
		if (self.value is None):
			self.value = self.Container();

		# Remove
		if (element.parent is not None):
			element.parent.remove_child(element);

		# Insert
		if (insert_pos is None):
			# Insert at end
			self.value.insert_at_end(element);
		else:
			# Insert at position
			self.value.insert(element, insert_pos);

		# Update parent and level
		element.parent = self;
		element.level = level_target;
		if (d.level_global):
			element.descriptor_level = level_target;
		else:
			element.descriptor_level = d.level;

		# Update size
		self._set_size(self.size + element.get_full_size());

	def remove_child(self, element):
		# Validate
		if (not self.is_child(element)):
			raise ElementError(ElementError.PARENT_INCORRECT);

		# Remove
		self.value.remove(element);

		# Remove
		self.__unparent(element);

		# Update size
		self._set_size(self.size - element.get_full_size());

	def is_child(self, element):
		return (not self.is_pointer() and element.child_id < len(self.value.children) and self.value.children[element.child_id] is element);

	def _decode_value(self):
		# Create container
		container = self.Container();

		# Read id
		while (True):
			# Find
			el = self.__read_element();
			if (el is None): break;

			# Add
			container.insert_at_end(el);

		# Done
		return container;

	def _encode(self, context):
		if ((self.descriptor.flags & ElementDescriptor.ROOT) == 0):
			return Element._encode(self, context);

		# Don't include "tag" info if it's the root
		self._encode_value(context);

	def _encode_value(self, context):
		for c in self.value.children:
			c._encode(context);

	def _set_value(self, value):
		if (isinstance(value, ( list , tuple ))):
			# Replace with children
			self.clear();
			for c in value:
				self.insert(c);
		else:
			# Invalid type
			raise ElementError(ElementError.VALUE_ERROR);

	def _to_xml_list(self, indent, indent_str):
		# Setup
		data = [];
		if ((self.descriptor.flags & ElementDescriptor.ROOT) == 0):
			data.append(u"{0:s}<{1:s}>\n".format(indent_str * indent, xml_escape(py_2or3_unicode_upcast(self.descriptor.name))));
			indent += 1;

		# Children
		for c in self.value.children:
			if (c.is_pointer()):
				data.extend(c._to_xml_pointer(indent, indent_str));
			else:
				data.extend(c._to_xml_list(indent, indent_str));

		# Closing
		if ((self.descriptor.flags & ElementDescriptor.ROOT) == 0):
			indent -= 1;
			data.append(u"{0:s}</{1:s}>\n".format(indent_str * indent, xml_escape(py_2or3_unicode_upcast(self.descriptor.name))));

		# Done
		return data;

	def __unparent(self, element):
		element.parent = None;
		element.next_sibling = None;
		element.previous_sibling = None;
		element.level = 0;
		element.descriptor_level = self.descriptor.level;
		element.child_id = 0;
		element.child_of_type_id = 0;

	def __read_element(self):
		# Read id
		context = self.context;
		id = context.read_id();
		if (id is None):
			return None;

		# Read size
		size,size_class = context.read_size();

		# Process
		schema = context.schema;
		d_level = self.descriptor_level + 1;
		decode_value = False;
		descriptor = None;
		if (id in schema.tags):
			# Get descriptor
			for d in schema.tags[id]:
				# Level validation
				if (d_level == d.level or (d.level_recursive and d_level >= d.level)):
					descriptor = d;
					break;

			if (descriptor is not None):
				# Version validate
				if (schema.version != 0 and descriptor.versions != 0 and (descriptor.versions & schema.version) == 0):
					context.warn(
						schema.strict_version_check,
						DecodeError.SCHEMA_VERSION_INVALID,
						u"{0:X} does not match any of {1:X}".format(schema.version, descriptor.versions)
					);

				if (not descriptor.pointer or not schema.pointers_enabled):
					# Check if context decode depth allows decoding
					if (context.decode_depth < 0):
						# Decode depth chain isn't active
						decode_value = True;
					elif (context.decode_depth > 0):
						# Decode depth chain is active
						context.decode_depth -= 1;
						decode_value = True;
					# Else, decode_depth = 0: don't decode

		if (descriptor is None):
			# None
			context.warn(
				schema.strict_missing_id,
				DecodeError.SCHEMA_ID_NOT_FOUND,
				u"[{0:s}]".format(ElementDescriptor.id_binary_to_str(id))
			);
			descriptor = ElementDescriptor(id, ElementDescriptor.id_binary_to_name(id), BINARY, d_level, 0, None, True, ElementDescriptor.MISSING);

		# Create element
		element = ElementClasses[descriptor.type](context, descriptor, self, self.level + 1, context.pos, size, size_class);

		# Element value
		if (decode_value):
			# Decode
			element._decode();
		else:
			# Skip
			skip_size = context.skip(size);
			if (skip_size != size):
				# Invalid data length
				context.warn_data_length(size, skip_size);

		# Done
		return element;



ElementClasses = (
	ElementInt,
	ElementUInt,
	ElementFloat,
	ElementString,
	ElementUnicode,
	ElementDate,
	ElementContainer,
	ElementBinary,
);



# Selector class
class Selector(object):
	class __Context(object):
		__re_whitespace = re.compile(r"\s*");
		__re_whitespace_end = re.compile(r"\s*$");
		__re_group = re.compile(r"(?::([\w_-]+)(\(\s*)?)|(\*)|([\w_-]+)|(\[\s*)", re.U);
		__re_separator = re.compile(r"\s*([,>+~])\s*|\s+");
		__re_paren_closer = re.compile(r"\s*\)");
		__re_bracket_closer = re.compile(r"\s*\]");
		__re_string_match = re.compile(r"\s*(?:([\"'])|([\w_-]+))", re.U);
		__re_nth_expression = re.compile(r"\s*(?:(even|odd)|(?:([+-]?\d+)|([+-]))?n(?:\s*([+-])\s*(\d+))?|([+-]?\d+))", re.I);

		__re_escape_codes = {
			u"\"": u"\"",
			u"\\": u"\\",
			u"'": u"'",
		};
		__re_escape_char = u"\\";


		def __init__(self, selector_str, pseudo_selectors):
			self.selector_str = selector_str;
			self.pos = self.__re_whitespace.match(selector_str).end();
			self.endpos = self.__re_whitespace_end.search(selector_str, self.pos).start();
			self.pseudo_selectors = pseudo_selectors;

		def parse_single_selector(self, em_pre):
			m = self.__re_group.match(self.selector_str, self.pos, self.endpos);
			if (m is not None):
				# Update position
				self.pos = m.end();

				# Check type
				g = m.groups();
				if (g[0] is not None):
					# Pseudo selector
					name = g[0];
					if (name not in self.pseudo_selectors):
						raise SelectorError(SelectorError.PSEUDO_SELECTOR_INVALID);

					ps = self.pseudo_selectors[name];
					paren = g[1] is not None;
					if (paren):
						# Validate
						if (not ps[1]):
							raise SelectorError(SelectorError.PSEUDO_SELECTOR_MISSING_PAREN);

						# Create
						em = ps[0](self);

						# Find closing
						m2 = self.__re_paren_closer.match(self.selector_str, self.pos);
						if (m2 is None):
							raise SelectorError(SelectorError.PSEUDO_SELECTOR_MISSING_PAREN_END);
						self.pos = m2.end();
					else:
						# Validate
						if (ps[1]):
							raise SelectorError(SelectorError.PSEUDO_SELECTOR_EXTRA_PAREN);

						# Create
						em = ps[0]();
				elif (g[2] is not None):
					# * selector
					if (em_pre is not None):
						raise SelectorError(SelectorError.TAG_NAME_SELECTOR_NOT_FIRST);
					em = Selector.ElementNameAny();
				elif (g[3] is not None):
					# Tag name selector
					if (em_pre is not None):
						raise SelectorError(SelectorError.TAG_NAME_SELECTOR_NOT_FIRST);
					em = Selector.ElementName(g[3]);
				else: # if (g[4] is not None):
					# [bracketed] selector
					name = g[4];
					em = Selector.Bracketed(self);

					# Find closing
					m2 = self.__re_bracket_closer.match(self.selector_str, self.pos);
					if (m2 is None):
						raise SelectorError(SelectorError.BRACKETED_MISSING_END);
					self.pos = m2.end();

				# Return
				return em;

			# None found
			return None;

		def parse_selector(self, target):
			# Create
			s_chain = Selector.SiblingChain();
			d_chain = Selector.DescendantChain(s_chain);
			target.entries.append(d_chain);
			em_pre = None;

			# Select
			while (True):
				em = self.parse_single_selector(em_pre);
				if (em is not None):
					# Link
					if (em_pre is None):
						s_chain.entries.append(em);
					else:
						em_pre.next = em;
					em_pre = em;
				else:
					# No element matcher was found
					if (em_pre is None):
						raise SelectorError(SelectorError.NO_SELECTOR_BEFORE_RELATIONSHIP);

					em_pre = None;
					m = self.__re_separator.match(self.selector_str, self.pos, self.endpos);
					if (m is not None):
						# Update position
						self.pos = m.end();

						# Check type
						g = m.groups();
						if (g[0] is not None):
							# Operator separated
							c = g[0][0];
							if (c == u","):
								# New group
								s_chain = Selector.SiblingChain();
								d_chain = Selector.DescendantChain(s_chain);
								target.entries.append(d_chain);
							elif (c == u">"):
								# Child
								s_chain = Selector.SiblingChain();
								d_chain.entries.append(s_chain);
								d_chain.relationships.append(Selector.DescendantChain.RELATIONSHIP_PARENT);
							elif (c == u"+"):
								# Following
								s_chain.relationships.append(Selector.SiblingChain.RELATIONSHIP_FOLLOWING);
							else: # if (c == u"~"):
								# Preceeded by
								s_chain.relationships.append(Selector.SiblingChain.RELATIONSHIP_PRECEEDED_BY);
						else:
							# Space separated
							s_chain = Selector.SiblingChain();
							d_chain.entries.append(s_chain);
							d_chain.relationships.append(Selector.DescendantChain.RELATIONSHIP_DESCENDANT);

					else:
						# Done
						break;

			# Check chaining
			if (len(s_chain.relationships) >= len(s_chain.entries)):
				raise SelectorError(SelectorError.NO_SELECTOR_AFTER_RELATIONSHIP);

		def parse_string(self):
			m = self.__re_string_match.match(self.selector_str, self.pos, self.endpos);
			if (m is None):
				raise SelectorError(SelectorError.STRING_EXPRESSION_INVALID);

			# Update position
			self.pos = m.end();

			# Process string
			g = m.groups();
			if (g[0] is None):
				# Simple
				return g[1];
			else:
				# Quoted
				quote = g[0];
				text = u"";
				p0 = self.pos;
				p1 = p0;
				escaped = False;
				while (p1 < self.endpos):
					c = self.selector_str[p1];

					# Escape
					if (escaped):
						escaped = False;
						if (c in self.__re_escape_codes):
							text += self.selector_str[p0 : p1 - 1];
							text += self.__re_escape_codes[c];
							p1 += 1;
							p0 = p1;
							continue;

					if (c == self.__re_escape_char):
						escaped = True;
					elif (c == quote):
						# Done
						text += self.selector_str[p0 : p1];
						self.pos = p1 + 1;
						return text;

					# Next
					p1 += 1;

				# Unterminated string
				self.pos = p1;
				raise SelectorError(SelectorError.STRING_EXPRESSION_NOT_CLOSED);

		def parse_nth_expression(self):
			# Match
			m = self.__re_nth_expression.match(self.selector_str, self.pos, self.endpos);
			if (m is None):
				raise SelectorError(SelectorError.NTH_EXPRESSION_INVALID);

			# Update position
			self.pos = m.end();

			# Process
			g = m.groups();
			if (g[0] is not None):
				# even or odd
				if (len(g[0]) == 3): # odd
					return ( 2 , 0 );
				else: # even
					return ( 2 , 1 );
			elif (g[5] is not None):
				# Single digit
				return ( 0 , int(g[5], 10) - 1 );
			else:
				# an+b form
				n1 = 1;
				if (g[1] is not None):
					n1 = int(g[1], 10);
				elif (g[2] == u"-"):
					n1 = -1;

				n2 = 0;
				if (g[4] is not None):
					n2 = int(g[4], 10);
					if (g[3] == u"-"):
						n2 = -n2;

				return ( n1 , n2 - 1 );



	class DescendantChain(object):
		RELATIONSHIP_PARENT = 0;
		RELATIONSHIP_DESCENDANT = 1;
		RELATIONSHIP_OPERATORS = ( u">" , u" " );

		def __init__(self, s_chain):
			self.entries = [ s_chain ];
			self.relationships = [];

		def matches(self, element):
			mode = self.RELATIONSHIP_PARENT;
			i = len(self.entries) - 1;
			while (True):
				if (not self.entries[i].matches(element)):
					if (mode == self.RELATIONSHIP_PARENT):
						return False;
					else:
						# Continue up parent chain
						element = element.parent;
						if (element is None):
							return False;
						continue;

				# Next
				if (i <= 0):
					return True;

				i -= 1;
				element = element.parent;
				if (element is None):
					return False;

				mode = self.relationships[i];

		def __str__(self):
			array = [ py_2or3_unicode_obj(self.entries[0]) ];

			i = 0;
			i_max = len(self.relationships);
			while (i < i_max):
				array.append(self.RELATIONSHIP_OPERATORS[self.relationships[i]]);
				i += 1;
				array.append(py_2or3_unicode_obj(self.entries[i]));

			return u"".join(array);

	class SiblingChain(object):
		RELATIONSHIP_FOLLOWING = 0;
		RELATIONSHIP_PRECEEDED_BY = 1;
		RELATIONSHIP_OPERATORS = ( u"+" , u"~" );

		def __init__(self):
			self.entries = [];
			self.relationships = [];

		def matches(self, element):
			mode = self.RELATIONSHIP_FOLLOWING;
			i = len(self.entries) - 1;
			while (True):
				if (not self.entries[i].matches_chained(element)):
					if (mode == self.RELATIONSHIP_FOLLOWING):
						return False;
					else:
						# Continue up sibling chain
						element = element.previous_sibling;
						if (element is None):
							return False;
						continue;

				# Next
				if (i <= 0):
					return True;

				i -= 1;
				element = element.previous_sibling;
				if (element is None):
					return False;

				mode = self.relationships[i];

		def __str__(self):
			array = [ self.entries[0].to_string_chained() ];

			i = 0;
			i_max = len(self.relationships);
			while (i < i_max):
				array.append(self.RELATIONSHIP_OPERATORS[self.relationships[i]]);
				i += 1;
				array.append(self.entries[i].to_string_chained());

			return u"".join(array);

	class ElementMatcher(object):
		def __init__(self):
			self.next = None;

		def matches(self, element):
			return False;

		def matches_chained(self, element):
			n = self;
			while (True):
				if (not n.matches(element)):
					return False;

				n = n.next;
				if (n is None):
					return True;

		def to_string_chained(self):
			array = [];
			n = self;
			while (True):
				array.append(py_2or3_unicode_obj(n));

				n = n.next;
				if (n is None):
					return u"".join(array);

	class ElementName(ElementMatcher):
		def __init__(self, name):
			Selector.ElementMatcher.__init__(self);
			self.name = name;

		def matches(self, element):
			return (element.get_tag_name() == self.name);

		def __str__(self):
			return py_2or3_unicode_upcast(self.name);

	class ElementNameAny(ElementMatcher):
		def __init__(self):
			Selector.ElementMatcher.__init__(self);

		def matches(self, element):
			return True;

		def __str__(self):
			return u"*";

	class Bracketed(ElementMatcher):
		def __init__(self, context):
			Selector.ElementMatcher.__init__(self);
			self.value = context.parse_string();

		def matches(self, element):
			return not element.is_pointer() and element.value_string_matches(self.value);

		def __str__(self):
			return u"[{0:s}]".format(Selector.escape_string(self.value));

	class PseudoRoot(ElementMatcher):
		def __init__(self):
			Selector.ElementMatcher.__init__(self);

		def matches(self, element):
			return (element.descriptor.flags & ElementDescriptor.ROOT) != 0;

		def __str__(self):
			return u":root";

	class PseudoEmpty(ElementMatcher):
		def __init__(self):
			Selector.ElementMatcher.__init__(self);

		def matches(self, element):
			return (not isinstance(element, ElementContainer) or element.is_pointer() or len(element.value.children) == 0);

		def __str__(self):
			return u":empty";

	class PseudoFirstChild(ElementMatcher):
		def __init__(self):
			Selector.ElementMatcher.__init__(self);

		def matches(self, element):
			return (element.child_id == 0);

		def __str__(self):
			return u":first-child";

	class PseudoLastChild(ElementMatcher):
		def __init__(self):
			Selector.ElementMatcher.__init__(self);

		def matches(self, element):
			return (element.parent is None or element.child_id == len(element.parent.value.children) - 1);

		def __str__(self):
			return u":last-child";

	class PseudoFirstOfType(ElementMatcher):
		def __init__(self):
			Selector.ElementMatcher.__init__(self);

		def matches(self, element):
			return (element.child_of_type_id == 0);

		def __str__(self):
			return u":first-of-type";

	class PseudoLastOfType(ElementMatcher):
		def __init__(self):
			Selector.ElementMatcher.__init__(self);

		def matches(self, element):
			return (element.parent is None or element.child_of_type_id == len(element.parent.value.children_of_type[element.get_tag_name()]) - 1);

		def __str__(self):
			return u":last-of-type";

	class PseudoNot(ElementMatcher):
		def __init__(self, context):
			Selector.ElementMatcher.__init__(self);
			self.matcher = context.parse_single_selector(None);
			if (self.matcher is None):
				raise SelectorError(SelectorError.NOT_SELECTOR_INVALID);

		def matches(self, element):
			return not self.matcher.matches(element);

		def __str__(self):
			return u":not({0:s})".format(py_2or3_unicode_obj(self.matcher));

	class PseudoNthChild(ElementMatcher):
		def __init__(self, context):
			Selector.ElementMatcher.__init__(self);
			self.counter = context.parse_nth_expression();

		def matches(self, element):
			# Setup
			a = self.counter[0];
			diff = element.child_id - self.counter[1];

			if (a == 0):
				# 0n+b == id
				return (diff == 0);
			else:
				# an+b == id, n >= 0
				return (diff % a) == 0 and (diff / a) >= 0;

		def __str__(self):
			return u":nth-child({0:s})".format(Selector.nth_expression_to_string(self.counter));

	class PseudoNthLastChild(ElementMatcher):
		def __init__(self, context):
			Selector.ElementMatcher.__init__(self);
			self.counter = context.parse_nth_expression();

		def matches(self, element):
			# Setup
			a = self.counter[0];
			if (element.parent is None):
				diff = 0;
			else:
				diff = (len(element.parent.value.children) - 1 - element.child_id);
			diff -= self.counter[1];

			if (a == 0):
				# 0n+b == id
				return (diff == 0);
			else:
				# an+b == id, n >= 0
				return (diff % a) == 0 and (diff / a) >= 0;

		def __str__(self):
			return u":nth-last-child({0:s})".format(Selector.nth_expression_to_string(self.counter));

	class PseudoNthOfType(ElementMatcher):
		def __init__(self, context):
			Selector.ElementMatcher.__init__(self);
			self.counter = context.parse_nth_expression();

		def matches(self, element):
			# Setup
			a = self.counter[0];
			diff = element.child_of_type_id - self.counter[1];

			if (a == 0):
				# 0n+b == id
				return (diff == 0);
			else:
				# an+b == id, n >= 0
				return (diff % a) == 0 and (diff / a) >= 0;

		def __str__(self):
			return u":nth-of-type({0:s})".format(Selector.nth_expression_to_string(self.counter));

	class PseudoNthLastOfType(ElementMatcher):
		def __init__(self, context):
			Selector.ElementMatcher.__init__(self);
			self.counter = context.parse_nth_expression();

		def matches(self, element):
			# Setup
			a = self.counter[0];
			if (element.parent is None):
				diff = 0;
			else:
				diff = (len(element.parent.value.children_of_type[element.get_tag_name()]) - 1 - element.child_of_type_id);
			diff -= self.counter[1];

			if (a == 0):
				# 0n+b == id
				return (diff == 0);
			else:
				# an+b == id, n >= 0
				return (diff % a) == 0 and (diff / a) >= 0;

		def __str__(self):
			return u":nth-last-of-type({0:s})".format(Selector.nth_expression_to_string(self.counter));

	class PseudoPointer(ElementMatcher):
		def __init__(self):
			Selector.ElementMatcher.__init__(self);

		def matches(self, element):
			return element.is_pointer();

		def __str__(self):
			return u":pointer";

	class PseudoType(ElementMatcher):
		__re_type_matcher = re.compile(r"\s*\w+\s*");

		def __init__(self, context):
			Selector.ElementMatcher.__init__(self);
			self.type = context.parse_string().lower();

		def matches(self, element):
			return (self.type == element.TYPE_STR);

		def __str__(self):
			return u":type({0:s})".format(Selector.escape_string(self.type));



	__pseudo_selectors = {
		# No parens
		"root": ( PseudoRoot , False ),
		"empty": ( PseudoEmpty , False ),
		"first-child": ( PseudoFirstChild , False ),
		"first-of-type": ( PseudoFirstOfType , False ),
		"last-child": ( PseudoLastChild , False ),
		"last-of-type": ( PseudoLastOfType , False ),

		# Parens
		"not": ( PseudoNot , True ),
		"nth-child": ( PseudoNthChild , True ),
		"nth-last-child": ( PseudoNthLastChild , True ),
		"nth-of-type": ( PseudoNthOfType , True ),
		"nth-last-of-type": ( PseudoNthLastOfType , True ),

		# Custom
		"pointer": ( PseudoPointer , False ),
		"type": ( PseudoType , True ),
	};



	__re_string_escaper = re.compile(r"[\"\'\\]");
	__re_string_escaper_map = {
		u"\"": u"\\\"",
		u"\\": u"\\\\",
		u"'": u"\\'",
	};
	__re_string_simple = re.compile(r"^([\w_-]+)$", re.U);

	@classmethod
	def escape_string(cls, text):
		if (cls.__re_string_simple.match(text)):
			return text;
		return u"\"{0:s}\"".format(cls.__re_string_escaper.sub(lambda m: cls.__re_string_escaper_map[m.group(0)], text));

	@classmethod
	def nth_expression_to_string(self, expr):
		a,b = expr;
		s = [];

		# First char
		if (a != 0):
			if (a == 1):
				s.append(u"n");
			elif (a == -1):
				s.append(u"-n");
			else:
				if (a == 2):
					if (b == 0):
						return u"odd";
					elif (b == 1):
						return u"even";
				s.append(u"{0:d}n".format(a));

		# Second char
		b += 1;
		if (b > 0):
			s.append(u"+{0:d}".format(b));
		elif (b < 0):
			s.append(u"{0:d}".format(b));

		# Done
		return u"".join(s);



	def __init__(self, selector):
		# Entry chain
		self.entries = [];

		# Create context
		context = self.__Context(selector, self.__pseudo_selectors);

		# Parse
		context.parse_selector(self);

		# Validate
		if (context.pos != context.endpos):
			raise SelectorError(SelectorError.END_OF_SELECTOR_NOT_REACHED);

	def matches(self, element):
		for e in self.entries:
			if (e.matches(element)):
				return True;

		return False;

	def select(self, element):
		# Check element
		if (self.matches(element)):
			return element;

		# Check children
		if (isinstance(element, ElementContainer) and not element.is_pointer()):
			for child in element.value.children:
				n = self.select(child);
				if (n is not None):
					return n;

		# None found
		return None;

	def select_all(self, element):
		elements = [];

		# Check element
		if (self.matches(element)):
			elements.append(element);

		# Check children
		if (isinstance(element, ElementContainer) and not element.is_pointer()):
			for child in element.value.children:
				elements.extend(self.select_all(child));

		# Found
		return elements;

	def __str__(self):
		return u",".join([ py_2or3_unicode_obj(e) for e in self.entries ]);

	def __repr__(self):
		return u"Selector({0:s})".format(repr(py_2or3_unicode_obj(self)));



# DOM creation
def decode(schema, stream):
	# Create context
	context = ReadContext(schema, stream);

	# Root container
	root = schema.root();
	root.context = context;
	root.value = root._decode_value();
	root.context = None;

	# Done
	return ( root , context );

def encode(element, stream, pointers_temporary=True):
	# Create context
	context = WriteContext(stream, pointers_temporary);

	# Write
	element._encode(context);


