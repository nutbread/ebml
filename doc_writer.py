import re, doc;

# Section id
section_id = u"";


# HTML escaping
__re_html_escaper = re.compile(r"[<>&]");
__re_html_escaper_attr = re.compile(r"[\"'<>&]");
__re_html_escaper_map = {
	u"\"": u"&quot;",
	u"'": u"&apos;",
	u"<": u"&lt;",
	u">": u"&gt;",
	u"&": u"&amp;",
};

def html_escape(value):
	return __re_html_escaper.sub(lambda m: __re_html_escaper_map[m.group(0)], value);
def html_escape_attr(value):
	return __re_html_escaper_attr.sub(lambda m: __re_html_escaper_map[m.group(0)], value);


# Text to id conversion
__re_id_remover = re.compile(r"^[^a-zA-Z0-9$_\+\.]+|[^a-zA-Z0-9$_\+\.]+$|'");
__re_id_replacer = re.compile(r"[^a-zA-Z0-9$_\+\.]+");
def text_to_id(text):
	rep_char = u"-";
	text = __re_id_remover.sub(u"", text);
	text = __re_id_replacer.sub(rep_char, text);

	if (len(text) == 0): return rep_char;
	return text;


# Text formatting
def format_text(text):
	return text;



# Writer classes
class NodeWriterHeader(doc.NodeWriter):
	def __init__(self, level):
		doc.NodeWriter.__init__(self);
		self.level = level;

	def process(self, node):
		global section_id;

		label = node.get_value_str();
		id = label;
		a = node.get_attribute(u"id");
		if (a is not None and a.value is not None):
			id = a.value;

		section_id = u'{0:s}.'.format(text_to_id(id));

		write(u'<h{0:d} id="{1:s}"><span class="hardlink_text">{2:s}<a class="hardlink" href="#{1:s}"></a></span></h{0:d}>'.format(self.level, html_escape_attr(id), html_escape(label)));

class NodeWriterParagraph(doc.NodeWriter):
	def __init__(self):
		doc.NodeWriter.__init__(self);

	def process(self, node):
		write(u'<p>{0:s}</p>'.format(format_text(node.get_value_str())));

class NodeWriterFunctionList(doc.NodeWriter):
	def __init__(self, is_member):
		doc.NodeWriter.__init__(self);
		self.is_member = is_member;

	def process(self, node):
		if (self.is_member):
			self.__process_member(node);
		else:
			self.__process_function(node);
	def group_start(self, node, pre):
		if (pre is None or not isinstance(pre, self.__class__)):
			write(u'<p><ul class="doc_list">');
	def group_end(self, node, next):
		if (next is None or not isinstance(next, self.__class__)):
			write(u'</ul></p>');

	def __process_function(self, node):
		global section_id;

		# Settings
		method_name = node.get_value_str();
		function_id = html_escape_attr(u'{0:s}{1:s}'.format(section_id, text_to_id(method_name)));

		# Setup params
		params = node.get_attributes(u"arg");

		# Source
		src = [
			u'<li><div class="doc_block" id="{0:s}"><input type="radio" class="doc_block_display_mode doc_block_display_mode_0" value="0" id="{0:s}.display.0" name="{0:s}.display.mode" checked /><input type="radio" class="doc_block_display_mode doc_block_display_mode_1" value="1" id="{0:s}.display.1" name="{0:s}.display.mode" />'.format(function_id),
			u'<div class="doc_block_indicator hardlink_text"><span class="doc_block_indicator_inner"><label class="doc_block_indicator_text" for="{0:s}.display.1"></label><label class="doc_block_indicator_text" for="{0:s}.display.0"></label></span><a class="doc_block_indicator_hardlink hardlink" href="#{0:s}"></a></div>'.format(function_id),
			u'<code class="doc_head doc_params_block{0:s}">'.format(u' doc_params_none' if (len(params) == 0) else u''),
		];

		# Object
		a = node.get_attribute(u"obj");
		if (a is not None):
			src.extend([
				u'<span class="doc_obj">{0:s}</span>'.format(html_escape(a.get_value_str())),
				u'<span class="doc_punct">.</span>',
			]);

		# Function name
		src.extend([
			u'<label class="doc_name" for="{0:s}.display.1"><span>{1:s}</span></label>'.format(function_id, html_escape(method_name)),
			u'<span class="doc_params_outer">(<span class="doc_params">',
		]);

		# Params
		for i in range(len(params)):
			# Parameter block
			param = params[i];

			param_classes = u'';
			a = param.get_attribute(u"keyword")
			if (a is not None):
				param_classes = u' doc_param_keyword';

			v = param.get_value_str();
			src.append(
				u'<span class="doc_param{1:s}"><span><a class="doc_param_name" href="#{0:s}.{2:s}"><span>{3:s}</span></a>'.format(function_id, param_classes, html_escape_attr(text_to_id(v)), html_escape(v))
			);

			a = param.get_attribute(u"default");
			if (a is not None):
				src.append(
					u'=<span class="doc_param_default">{0:s}</span>'.format(html_escape(a.get_value_str()))
				);

			src.append(u'</span>');
			if (i + 1 < len(params)): src.append(u', ');
			src.append(u'</span>');

		# Params closer
		src.append(u'</span>');
		if (len(params) > 0): src.append(u'<span class="doc_params_placeholder">...</span>');
		src.append(u')</span>');
		return_attr = node.get_attribute(u"return");
		if (return_attr is not None):
			src.append(u'<span class="doc_return_container"> : <a class="doc_return" href="#{0:s}.return"><span>{1:s}</span></a></span>'.format(function_id, html_escape(return_attr.get_value_str())));
		src.append(u'</code>');


		# Descriptions
		src.append(u'<div class="doc_descriptions">');
		a = node.get_attribute(u"desc");
		if (a is not None):
			src.append(
				u'<div class="doc_description doc_description_main">{0:s}</div>'.format(format_text(a.get_value_str()))
			);

		# Param descriptions
		for param in params:
			# Skip
			if (param.get_attribute(u"desc") is None and param.get_attribute(u"type") is None):
				continue;

			# Write
			v = param.get_value_str();
			src.append(
				u'<div class="doc_description doc_description_param" id="{0:s}.{1:s}"><code><a class="doc_description_param_name" href="#{0:s}.{1:s}"><span>{2:s}</span></a>'.format(function_id, html_escape_attr(text_to_id(v)), html_escape(v))
			);

			a = param.get_attribute(u"type");
			if (a is not None):
				src.append(u'<span class="doc_param_type"> : {0:s}</span>'.format(html_escape(a.get_value_str())));
			src.append(u'</code>');


			a = param.get_attribute(u"desc");
			if (a is not None):
				src.append(u'<div class="doc_description_body">{0:s}</div>'.format(format_text(a.get_value_str())));

			src.append(u'</div>');

		# Return description
		if (return_attr is not None):
			src.append(
				u'<div class="doc_description doc_description_return" id="{0:s}.{1:s}"><code><a class="doc_description_return_name" href="#{0:s}.{1:s}"><span>{1:s}</span></a>'.format(function_id, u'return')
			);
			if (return_attr.value is not None):
				src.append(u'<span class="doc_param_type"> : {0:s}</span>'.format(html_escape(return_attr.value)));
			src.append(u'</code>');


			a = return_attr.get_attribute(u"desc");
			if (a is not None):
				src.append(u'<div class="doc_description_body">{0:s}</div>'.format(format_text(a.get_value_str())));

			src.append(u'</div>');

		src.append(u'</div>');


		# Close
		src.append(u'</div></li>');

		# Done
		write(u''.join(src));
	def __process_member(self, node):
		global section_id;

		# Id
		a = node.get_attribute(u"id");
		if (a is None):
			main_id = u'{0:s}{1:s}'.format(section_id, text_to_id(node.get_value_str()));
		else:
			main_id = u'{0:s}{1:s}'.format(section_id, text_to_id(a.get_value_str()));
		main_id = html_escape_attr(main_id);

		# Setup node array
		node_members = [ node ] + node.get_attributes(u"also");
		member_obj = node.get_attribute(u"obj");


		# Setup
		src = [
			u'<li><div class="doc_block" id="{0:s}"><input type="radio" class="doc_block_display_mode doc_block_display_mode_0" value="0" id="{0:s}.display.0" name="{0:s}.display.mode" checked /><input type="radio" class="doc_block_display_mode doc_block_display_mode_1" value="1" id="{0:s}.display.1" name="{0:s}.display.mode" />'.format(main_id),
			u'<div class="doc_block_indicator hardlink_text"><span class="doc_block_indicator_inner"><label class="doc_block_indicator_text" for="{0:s}.display.1"></label><label class="doc_block_indicator_text" for="{0:s}.display.0"></label></span><a class="doc_block_indicator_hardlink hardlink" href="#{0:s}"></a></div>'.format(main_id),
		];


		# Header(s)
		src.append(u'<div class="doc_head">');
		for i in range(len(node_members)):
			member = node_members[i];
			id = html_escape_attr(u'{0:s}{1:s}'.format(section_id, text_to_id(member.get_value_str())));

			src.append('<div class="doc_member_entry" id="{0:s}">'.format(id));

			if (member_obj is not None):
				src.extend([
					u'<span class="doc_obj">{0:s}</span>'.format(html_escape(member_obj.get_value_str())),
					u'<span class="doc_punct">.</span>',
				]);

			src.append(
				u'<span class="doc_member"><span><label class="doc_member_name" for="{0:s}.display.1"><span>{1:s}</span></label>'.format(main_id, html_escape(member.get_value_str()))
			);

			a = member.get_attribute(u"value");
			if (a is not None):
				src.append(u'=<span class="doc_member_value">{0:s}</span>'.format(html_escape(a.get_value_str())));

			a = member.get_attribute(u"type");
			if (a is not None):
				src.append(u'<span class="doc_return_container"> : {0:s}</span>'.format(html_escape(a.get_value_str())));

			src.append(u'</span></span>');
			if (i + 1 < len(node_members)): src.append(u',');
			src.append(u'</div>');
		src.append(u'</div>');


		# Description
		a = node.get_attribute(u"desc");
		if (a is not None):
			description_id = u'{0:s}.description'.format(main_id);

			src.append(u'<div class="doc_descriptions"><div class="doc_description doc_description_main">');
			src.append(format_text(a.get_value_str()));
			src.append(u'</div></div>');


		# Complete
		src.append(u'</div></li>');

		# Write
		write(u''.join(src));



# Document writer
write = None;
def process_doc(filename, write_fn):
	global write;
	write = write_fn;

	f = open(filename, u"rb");
	par = doc.Node.parse(f);
	f.close();

	doc.NodeWriter.process_node(par, descriptor_main);



# Main descriptor
descriptor_main = doc.NodeWriter.Descriptor()
descriptor_main.define(u"h4", NodeWriterHeader, 4);
descriptor_main.define(u"h6", NodeWriterHeader, 6);
descriptor_main.define(u"p", NodeWriterParagraph);
descriptor_main.define(u"fn", NodeWriterFunctionList, False);
descriptor_main.define(u"member", NodeWriterFunctionList, True);

