from glob import glob
from xml.etree import ElementTree as ET
from xml.dom import minidom

ET.register_namespace('d', 'http://www.apple.com/DTDs/DictionaryService-1.0.rng')
out = ET.ElementTree(ET.Element('d:dictionary'))
out.getroot().set('xmlns', 'http://www.w3.org/1999/xhtml')
out.getroot().set('xmlns:d', 'http://www.apple.com/DTDs/DictionaryService-1.0.rng')

for frame_file in glob('propbank-frames/frames/*.xml'):
    for predicate in ET.parse(frame_file).findall('predicate'):
        for roleset in predicate.findall('roleset'):
            role_name = roleset.get('id').replace('_', '-').replace('.', '-')
            desc = roleset.get('name')
            entry = ET.SubElement(out.getroot(), 'd:entry')
            entry.set('id', role_name)
            entry.set('d:title', role_name)
            ET.SubElement(entry, 'd:index').set('d:value', role_name)
            ET.SubElement(entry, 'd:index').set('d:value', predicate.get('lemma'))
            ET.SubElement(entry, 'h1').text = role_name
            ET.SubElement(entry, 'p').text = desc
            for alias in roleset.find('aliases').findall('alias'):
                ET.SubElement(entry, 'd:index').set('d:value', alias.text)
            for role in roleset.find('roles').findall('role'):
                name = ':ARG{}'.format(role.get('n'))
                desc = role.get('descr')
                ET.SubElement(entry, 'p').text = '{} -- {}'.format(name, desc)
            examples = roleset.findall('example')
            if examples:
                ET.SubElement(entry, 'h4').text = 'Examples'
                for ex in examples:
                    ET.SubElement(ET.SubElement(entry, 'p'), 'b').text = ex.get('name')
                    ET.SubElement(entry, 'p').text = ex.find('text').text
                    for arg in ex.findall('arg'):
                        if arg.get('f') == '':
                            if arg.get('n') is None:
                                ET.SubElement(entry, 'p').text = arg.text
                            else:
                                ET.SubElement(entry, 'p').text = ':ARG{} -- {}'.format(arg.get('n'), arg.text)
                        else:
                            ET.SubElement(entry, 'p').text = ':{} -- {}'.format(arg.get('f'), arg.text)

out.write('PropBank.xml')
x = minidom.parse('PropBank.xml')
with open('PropBank.xml', 'w') as f:
    x.writexml(f, '', '  ', '\n')

"""
<d:entry id="dictionary_application" d:title="Dictionary application">
	<d:index d:value="Dictionary application"/>
	<h1>Dictionary application </h1>
	<p>
		An application to look up dictionary on Mac OS X.<br/>
	</p>
	<span class="column">
		The Dictionary application first appeared in Tiger.
	</span>
	<span class="picture">
		It's application icon looks like below.<br/>
		<img src="Images/dictionary.png" alt="Dictionary.app Icon"/>
	</span>
</d:entry>
"""