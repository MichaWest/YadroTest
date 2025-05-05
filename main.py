from json_creator import JSON_creator
from xml_creator import XML_creator
import traceback



try:
    input_path = "input/test_input.xml"
    with open(input_path, 'r') as f:
        creator_xml = XML_creator(input_path, "out/config.xml")
        creator_json = JSON_creator(input_path, "out/meta.json")

        creator_xml.create_file()
        creator_json.create_file()
except Exception as err:
    traceback.print_exc()
    print(f"Unexpected {err=}, {type(err)=}")
