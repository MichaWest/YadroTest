import xml.etree.ElementTree as ET

'''
Так как написано и встроенно не одна бибилотека для работы с xml файлами.
Было принято решение: написать класс, который бы реализовал интерфейс,
необходимый классам JSON-creator и XML-creator. Чтобы в дальнейшем,
если будут причины перейти на другую библиотеку, переход был проще
'''
class XML_reader:
    '''
    Парсим входной файл с помощью выбранной библиотеки
    Возвращаем ошибку, если входной файл пустой
    '''
    def __init__(self, path: str):
        try:
            self.data : ElementTree  = ET.parse(path)
        except ET.ParseError:
            raise NameError("Parse error")


    def get_attribute(self, element):
        return element.attrib

    def get_kids(self, element):
        kids = []
        for k in element:
            kids.append(k)
        return kids

    def get_tag_name(self, element):
        return element.tag

    def get_root(self):
        return self.data.getroot()

