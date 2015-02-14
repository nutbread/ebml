# Imports
import sys, ebml, mkv;



# Multi versioning
if (sys.version_info[0] == 3):
	# Version 3
	import io;
	py_2or3_StringStream = io.BytesIO;
else:
	# Version 2
	import StringIO;
	py_2or3_StringStream = StringIO.StringIO;



# Test a generic schema
def test_schema():
	# Simple schema
	schema = ebml.Schema();
	schema.define(b"\x1A\x45\xDF\xA3", u"Container", ebml.CONTAINER, 0);
	schema.define(b"\x42\x86", u"Int", ebml.INT, 1);
	schema.define(b"\x42\xF7", u"Uint", ebml.UINT, 1);
	schema.define(b"\x42\xF2", u"Float", ebml.FLOAT, 1);
	schema.define(b"\x42\xF3", u"String", ebml.STRING, 1);
	schema.define(b"\x42\x82", u"Unicode", ebml.UNICODE, 1);
	schema.define(b"\x42\x87", u"Date", ebml.DATE, 1);
	schema.define(b"\x42\x85", u"Binary", ebml.BINARY, 1);

	# Create nodes
	root = schema.root();
	el_int = schema.element(u"Int", -0xff80000);
	el_uint = schema.element(u"Uint", 1012341234123423);
	el_uint2 = schema.element(u"Uint", 32);
	el_float = schema.element(u"Float", 32.0);
	el_string = schema.element(u"String", "words");
	el_unicode = schema.element(u"Unicode", u"unicode \u3042 words");
	el_date = schema.element(u"Date", -10000000000);
	el_binary = schema.element(u"Binary", b"asdf");
	el_cont = schema.element(u"Container", [ el_uint2 ]);

	# Append
	el_cont.insert(el_int);
	el_cont.insert(el_uint);
	el_cont.insert(el_float);
	el_cont.insert(el_string);
	el_cont.insert(el_unicode);
	el_cont.insert(el_date);
	el_cont.insert(el_binary);

	# Add to root
	root.insert(el_cont);

	# Remove an element
	el_uint2.remove();

	# Output to a string stream
	sout = py_2or3_StringStream();
	ebml.encode(root, sout);

	# Convert to an input stream
	sin = py_2or3_StringStream(sout.getvalue());
	c, ctx = ebml.decode(schema, sin);

	# Status
	sys.stdout.write(u"Outputs match: {0:s}\n".format(str(root.to_xml() == c.to_xml())));


# Test a file
def test_file(filename):
	# Test file
	f = open(filename, u"rb");


	# Decode
	root, ctx = ebml.decode(mkv.schema, f);


	# Pointer methods performed on a data cluster
	first_data_cluster = ebml.Selector(u"Cluster:nth-of-type(1)").select(root);
	sys.stdout.write(u"Is pointer: {0:s}\n".format(str(first_data_cluster.is_pointer())));
	sys.stdout.write(u"     Value: {0:s}\n".format(repr(first_data_cluster.get())));
	sys.stdout.write(u"Is pointer: {0:s}\n".format(str(first_data_cluster.is_pointer())));
	first_data_cluster.to_pointer();
	sys.stdout.write(u"     Value: {0:s}\n".format(repr(first_data_cluster.value)));
	sys.stdout.write(u"Is pointer: {0:s}\n".format(str(first_data_cluster.is_pointer())));


	# Output to xml
	f_xml = open(u"test.xml", u"wb");
	f_xml.write(root.to_xml().encode(u"utf-8"));
	f_xml.close();

	# Output
	f_out = open(u"test-out.mkv", u"wb");
	ebml.encode(root, f_out)
	f_out.close();

	# Close input
	f.close();



# Main
def main():
	# Schema test
	test_schema();


	# MKV test
	print("=" * 80);
	test_file(u"media/test.mkv");
	print("=" * 80);
	test_file(u"media/test.webm");
	print("=" * 80);



	# Done
	return 0;



# Execute
if (__name__ == "__main__"): sys.exit(main());


