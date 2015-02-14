# Imports
import re, sys, json, xml.dom.minidom;



# Settings
re_name_normalize = re.compile(r"(^[^a-zA-Z]|[^a-zA-Z0-9_])");
types = {
	u"integer": u"INT",
	u"uinteger": u"UINT",
	u"float": u"FLOAT",
	u"string": u"STRING",
	u"utf-8": u"UNICODE",
	u"date": u"DATE",
	u"master": u"CONTAINER",
	u"binary": u"BINARY",
};
versions = {
	u"1": u"V1",
	u"2": u"V2",
	u"3": u"V3",
	u"4": u"V4",
	u"WEBM": u"VWEBM",
};
validators = {
	u"not 0": u"__validator_not_0",
	u"> 0": u"__validator_gt_0",
	u">0": u"__validator_gt_0",
	u"0-1": u"__validator_0_or_1",
	u"1-254": u"__validator_1_thru_254",
};
pointer_tags = {
	u"Cluster": True,
};



# Read document
# https://github.com/Matroska-Org/foundation-source/blob/master/spectool/specdata.xml
f = open(u"specdata.xml", u"rb");
spec_doc = f.read();
f.close();
spec_doc = xml.dom.minidom.parseString(spec_doc);



# Create source
source = [
	u"__validator_not_0 = (lambda x: x != 0);",
	u"__validator_gt_0 = (lambda x: x > 0);",
	u"__validator_0_or_1 = (lambda x: x >= 0 and x <= 1);",
	u"__validator_1_thru_254 = (lambda x: x >= 1 and x <= 254);",
	u"",
	u"schema = ebml.Schema();",
];



# Process
for element in spec_doc.getElementsByTagName(u"table")[0].getElementsByTagName(u"element"):
	# Versioning
	minver = None;
	maxver = None;

	if (element.hasAttribute(u"minver")):
		minver = int(element.getAttribute(u"minver"), 10);
	if (element.hasAttribute(u"maxver")):
		maxver = int(element.getAttribute(u"maxver"), 10);

	# Skip?
	if (minver is None):
		if (maxver is None):
			continue;
		minver = 1;
	else:
		maxver = 4;
	if (minver <= 0 or maxver < minver):
		continue;

	# Values
	webm = not (element.hasAttribute(u"webm") and int(element.getAttribute(u"webm"), 10) == 0);
	name = re_name_normalize.sub(u"", element.getAttribute(u"name"));
	id = element.getAttribute(u"id")[2:];
	id = u"".join([ u"\\x{0:s}".format(id[i : i + 2]) for i in range(0, len(id), 2) ]);
	value_type = types[element.getAttribute(u"type")];
	mandatory = element.hasAttribute(u"mandatory") and int(element.getAttribute(u"mandatory"), 10) != 0;
	multiple = element.hasAttribute(u"multiple") and int(element.getAttribute(u"multiple"), 10) != 0;
	default_value = None;
	if (element.hasAttribute(u"default")):
		default_value = element.getAttribute(u"default");
	level = int(element.getAttribute(u"level"), 10);
	if (level < 0):
		level = u'u"g"';
	elif (element.hasAttribute(u"recursive") and int(element.getAttribute(u"recursive"), 10) != 0):
		level = u'u"{0:d}+"'.format(level);
	else:
		level = str(level);
	value_range = None;
	if (element.hasAttribute(u"range")):
		value_range = element.getAttribute(u"range");

	# Process
	version_str = u"";
	for v in range(minver, maxver + 1):
		v = str(v);
		if (len(version_str) > 0): version_str += u"|";
		version_str += u"{0:s}".format(versions[v]);
	if (webm):
		v = u"WEBM";
		if (len(version_str) > 0): version_str += u"|";
		version_str += u"{0:s}".format(versions[v]);

	validator_str = u"None";
	if (value_range is not None):
		validator_str = validators[value_range];

	pointer_str = u"False";
	if (name in pointer_tags and pointer_tags[name] == True):
		pointer_str = u"True";

	# Update source
	source.append(u'schema.define(b"{0:s}", u"{1:s}", ebml.{2:s}, {3:s}, {4:s}, {5:s}, {6:s});'.format(id, name, value_type, level, version_str, validator_str, pointer_str));




# Output
sys.stdout.write(u"{0:s}\n".format(u"\n".join(source)).encode(u"utf-8"));
sys.exit(0);
