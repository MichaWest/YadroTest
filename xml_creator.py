import os

import xml.etree.ElementTree as ET
from xml_reader import XML_reader



class XML_node:

    def __init__(self, name: str):
        self.parameters: dict = {}
        self.name = name
        self.children: list[XML_node] = []

    def add_param(self, param_name: str, param_val: str) -> None:
        self.parameters[param_name] = param_val

    def add_child(self, child) -> None:
        self.children.append(child)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        res_1 = self.parameters == other.parameters
        res_2 = self.children.sort() == other.children.sort()
        res_3 = self.name == other.name
        return res_3 and res_1 and res_2


class XML_creator:

    def __init__(self, input_path: str, output_path: str = "src/out/config.xml"):
        filename, file_extension = os.path.splitext(output_path)

        if file_extension != ".xml":
            raise ValueError("The path must point to the format file .xml")

        self.output_path = output_path
        self.xml_reader: XML_reader = XML_reader(input_path)

    def create_file(self):
        self.__define_tag_dict__()
        root_tag = self.__get_root_tag__()
        root_node = self.__create_structure__(root_tag)
        self.__write_output__(root_node)

        #self.__write_output__(self.__create_structure__(self.__get_root_tag__()))


    def __write_output__(self, root_node: XML_node):
        root_tag = self.__create_output__(root_node)
        tree = ET.ElementTree(root_tag)
        ET.indent(tree, ' ')
        tree.write(self.output_path, encoding="utf-8", xml_declaration=True, short_empty_elements=False)


    '''
    Создаем дерево элементов 
    '''
    def __create_output__(self, root_node: XML_node):
        root_tag = ET.Element(root_node.name)
        self.__create_tag_param__(root_tag, root_node)
        kids = root_node.children
        for k in kids:
            self.__create_subelement__(root_tag, k)

        return root_tag

    def __create_tag_param__(self, tag, node):
        for p in list(node.parameters):
            param_tag = ET.SubElement(tag, p)
            param_tag.text = node.parameters[p]

    def __create_subelement__(self, ptag, node: XML_node):
        tag = ET.SubElement(ptag, node.name)
        self.__create_tag_param__(tag, node)
        for k in node.children:
            self.__create_subelement__(tag, k)


    '''
    Определяем дерево элементов (XMl_Node)
    '''
    def __create_structure__(self, tag) -> XML_node:
        tag_attrs = self.xml_reader.get_attribute(tag)
        tag_name = tag_attrs['name']
        xml_node = XML_node(tag_name)

        xml_node = self.__write_parameters__(tag, xml_node)

        # находим детей и запускаем для них функцию create_xml_tree
        temp_dict = {k: v for k, v in self.aggregation_tags.items() if (v['target'] == tag_attrs['name'])}
        source_dict = {}
        for t in list(temp_dict):
            source_dict.update({k: v for k, v in self.class_tags.items() if (v['name'] == self.aggregation_tags[t]['source'])})

        for t in list(source_dict):
            source_node = self.__create_structure__(t)
            xml_node.add_child(source_node)

        return xml_node

    def __write_parameters__(self, tag, xml_node: XML_node) -> XML_node:
        for key in self.xml_reader.get_kids(tag):
            key_attribute = self.xml_reader.get_attribute(key)
            xml_node.add_param(key_attribute['name'], key_attribute['type'])

        return xml_node

    def __define_tag_dict__(self):
        root = self.xml_reader.get_root()
        kids = self.xml_reader.get_kids(root)

        self.class_tags = {}
        self.aggregation_tags = {}

        for k in kids:
            if self.xml_reader.get_tag_name(k) == 'Class':
                self.class_tags[k] = self.xml_reader.get_attribute(k)
            if self.xml_reader.get_tag_name(k) == 'Aggregation':
                self.aggregation_tags[k] = self.xml_reader.get_attribute(k)

    def __get_root_tag__(self):
        for k in list(self.class_tags):
            if self.xml_reader.get_attribute(k)['isRoot'] == 'true':
                return k