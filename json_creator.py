import json
import os
from xml_reader import XML_reader

class JSON_node:

    def __init__(self, name: str = '', is_root: bool = False, doc: str = '', param=None):
        if param is None:
            param = []
        self.class_name: str = name
        self.documentation: str = doc
        self.isRoot: bool = is_root
        self.max = None
        self.min = None
        self.parameters: list[{str: str}] = param

    def add_param(self, param_name: str, param_type: str):
        self.parameters.append({param_name: param_type})

    def get_json_dict(self):
        json_dict = {'class': self.class_name}
        json_dict.update(self.__dict__.copy())
        del json_dict['class_name']
        if self.max is None:
            del json_dict['max']
        if self.min is None:
            del json_dict['min']
        return json_dict

    def __eq__(self, other):
        if type(other) is JSON_node:
            return self.class_name == other.class_name and \
                   self.isRoot == other.isRoot and \
                   self.documentation == other.documentation and \
                   self.parameters == other.parameters
        else:
            return False

    def __len__(self):
        return len(self.__dict__) + len(self.parameters) + 1

    def __str__(self):
        return self.class_name+" "+str(self.isRoot)+" "+self.documentation+" "+str(self.parameters)


def get_max_min_sourceMultiplicity(input_str: str):
    res = input_str.split("..")
    if len(res) == 2:
        return (res[0]), (res[1])
    else:
        return (res[0]), (res[0])


class JSON_creator:

    def __init__(self, input_path: str, output_path: str = "out/config.json"):
        filename, file_extension = os.path.splitext(output_path)

        if file_extension != ".json":
            raise ValueError("The path must point to the format file.json")

        self.list_node: list[JSON_node] = []
        self.output_path = output_path
        self.xml_reader: XML_reader = XML_reader(input_path)

    def create_file(self) -> list:
        json_list = []

        self.__define_tag_dict__()
        root_tag = self.__find_root_element__()

        self.__create_structure__(root_tag)
        json_list = self.__write_out_structure__()

        with open(self.output_path, mode='w') as f:
            f.write(json.dumps(json_list, indent=1))
        return json_list

    def __create_structure__(self, tag) -> JSON_node:
        node = JSON_node()
        self.__define_fields__(node, tag)

        tag_attr = self.xml_reader.get_attribute(tag)

        temp_dict = {k: v for k, v in self.aggregation_tags.items() if (v['target']==tag_attr['name'])}
        source_dict = {}
        for t in list(temp_dict):
            source_dict.update({k: v for k, v in self.class_tags.items() if (v['name']==self.aggregation_tags[t]['source'])})

        for t in list(source_dict):
            self.__create_structure__(t)

        self.list_node.append(node)
        return node

    def __define_fields__(self, node: JSON_node, tag) -> JSON_node:
        # определяем поле 'name'
        attrs = self.class_tags[tag]
        tag_name = attrs['name']
        node.class_name = tag_name

        # определяем поле documentation
        tag_doc = attrs['documentation']
        node.documentation = tag_doc

        # определяем поле isRoot
        tag_is_root = attrs['isRoot']
        node.isRoot = (tag_is_root == 'true')

        # определяем поле parameters
        attribute_tags = self.xml_reader.get_kids(tag)
        for t in attribute_tags:
            t_attrs = self.xml_reader.get_attribute(t)
            attr_name = t_attrs['name']
            attr_type = t_attrs['type']
            node.parameters.append({'name': attr_name, 'type': attr_type})


        for t in list(self.aggregation_tags):
            t_attrs = self.aggregation_tags[t]
            if t_attrs['source'] == tag_name:
                min_val, max_val = get_max_min_sourceMultiplicity(t_attrs['sourceMultiplicity'])
                node.max = max_val
                node.min = min_val

        #aggregation_tags = self.BS_data.findAll('Aggregation', {'target': tag_name})
        for t in list(self.aggregation_tags):
            t_attrs = self.aggregation_tags[t]
            if t_attrs['target'] == tag_name:
                child_name = t_attrs['source']
                node.parameters.append({'name': child_name, 'type': 'class'})
        return node

    def __write_out_structure__(self) -> list:
        json_list = []
        for n in self.list_node:
            json_list.append(n.get_json_dict())
        return json_list

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

    def __find_root_element__(self):
        for k in self.class_tags:
            if self.xml_reader.get_attribute(k)['isRoot'] == 'true':
                return k

