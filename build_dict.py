from glob import glob
from xml.etree import ElementTree as ET
from xml.dom import minidom
import itertools


def parse_propbank_xml(frame_file):
    for predicate in ET.parse(frame_file).findall('predicate'):
        for roleset in predicate.findall('roleset'):
            result = {}
            result['name'] = roleset.get('id').replace('_', '-').replace('.', '-')
            result['desc'] = roleset.get('name')
            result['lemma'] = predicate.get('lemma')
            result['aliases'] = []
            for alias in roleset.find('aliases').findall('alias'):
                result['aliases'].append(alias.text)
            result['roles'] = []
            for role in roleset.find('roles').findall('role'):
                result['roles'].append({
                    'name': ':ARG{}'.format(role.get('n')),
                    'desc': role.get('descr')
                })
            result['examples'] = []
            for ex in roleset.findall('example'):
                result['examples'].append({
                    'name': ex.get('name'),
                    'text': ex.find('text').text,
                    'args': []
                })
                for arg in ex.findall('arg'):
                    if arg.get('f') == '':
                        if arg.get('n') is None:
                            result['examples'][-1]['args'].append({'name': ''})
                        else:
                            result['examples'][-1]['args'].append({'name': ':ARG{}'.format(arg.get('n'))})
                    else:
                        result['examples'][-1]['args'].append({'name': ':{}'.format(arg.get('f'))})
                    result['examples'][-1]['args'][-1]['value'] = arg.text
            yield result


def generate_dict_xml(output_file, frames):
    ET.register_namespace('d', 'http://www.apple.com/DTDs/DictionaryService-1.0.rng')
    out = ET.ElementTree(ET.Element('d:dictionary'))
    out.getroot().set('xmlns', 'http://www.w3.org/1999/xhtml')
    out.getroot().set('xmlns:d', 'http://www.apple.com/DTDs/DictionaryService-1.0.rng')

    for frame in frames:
        entry = ET.SubElement(out.getroot(), 'd:entry')
        entry.set('id', frame['name'])
        entry.set('d:title', frame['name'])
        entry = ET.SubElement(entry, 'div')
        entry.set('class', 'entry')
        ET.SubElement(entry, 'd:index').set('d:value', frame['name'])
        ET.SubElement(entry, 'd:index').set('d:value', frame['lemma'])
        for alias in frame['aliases']:
            ET.SubElement(entry, 'd:index').set('d:value', alias)

        ET.SubElement(entry, 'h1').text = frame['name']
        e = ET.SubElement(entry, 'div')
        e.text = frame['desc']
        e.set('class', 'desc')

        dl = ET.SubElement(entry, 'dl')
        for role in frame['roles']:
            ET.SubElement(dl, 'dt').text = role['name']
            ET.SubElement(dl, 'dd').text = role['desc']
        
        d = ET.SubElement(entry, 'div')
        d.set('class', 'subtle')
        d.set('d:priority', '1')
        for i, ex in enumerate(frame['examples']):
            e = ET.SubElement(d, 'p')
            ET.SubElement(e, 'i').text = 'Ex {} ({}): '.format(i+1, ex['name'])
            ET.SubElement(e, 'span').text = ex['text']
            dl = ET.SubElement(d, 'dl')
            for arg in ex['args']:
                ET.SubElement(dl, 'dt').text = arg['name']
                ET.SubElement(dl, 'dd').text = arg['value']

    out.write(output_file)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Builds an Apple dictionary file from PropBank XML.')
    parser.add_argument('src_files', help='glob expression to locate PropBank XML files.')
    parser.add_argument('out_file', help='file path of output Apple Dictionary XML file.')
    args = parser.parse_args()

    frames = itertools.chain(*(parse_propbank_xml(f) for f in glob(args.src_files)))
    generate_dict_xml(args.out_file, frames)


















