from html.parser import HTMLParser
from pprint import pprint
import requests
import time


def tuplelist_to_dict(tuplelist):
    dict_ = {}

    for key, value in tuplelist:
        if key in dict_:  # There exists a key in the dict already
            if isinstance(dict_[key], list):  # The value at this key is already a list
                dict_[key].append(value)
            else:
                dict_[key] = [dict_[key], value]  # Make a list with the existing value plus the new value
        else:
            dict_[key] = value

    return dict_


class HTMLNode:
    def __init__(self, tagtype, attrs=None, children=None):
        self.type = tagtype
        self.attrs = {} if attrs is None else attrs
        self.children = [] if children is None else children

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        children = ""
        for child in self.children:
            children += "\n    {}".format(str(child).replace("\n", "\n    "))
        if children:
            children += "\n"
        else:
            children = "[]"

        return "HTMLNode(type={}, attrs={}, children={})".format(self.type, self.attrs, children)


class PrettySauce(HTMLParser):
    void_elements = ["area", "base", "br", "col", "embed", "hr", "img", "input",
                     "link", "meta", "param", "source", "track", "wbr"]

    def __init__(self):
        super().__init__()
        self._dom_stack = []
        self.dom = []

    def _push(self, elem):
        self._dom_stack.append(elem)

    def _pop(self):
        return self._dom_stack.pop() if len(self._dom_stack) > 0 else None

    def _peek(self):
        return self._dom_stack[-1] if len(self._dom_stack) > 0 else None

    def handle_starttag(self, tag, attrs):
        if tag in self.void_elements:
            self.handle_startendtag(tag, attrs)
        else:
            node = HTMLNode(tag, attrs=tuplelist_to_dict(attrs))
            self._push(node)

    def handle_endtag(self, tag):
        node = self._pop()
        if node is None:
            raise ValueError("Got {} end tag without matching start tag".format(tag))
        if node.type != tag:
            raise ValueError("Expected {} end tag, got {}".format(node.type, tag))

        parent = self._peek()
        if parent is not None:
            parent.children.append(node)
        else:
            self.dom.append(node)

    def handle_startendtag(self, tag, attrs):
        node = HTMLNode(tag, attrs=tuplelist_to_dict(attrs))
        parent = self._peek()
        if parent is not None:
            parent.children.append(node)
        else:
            self.dom.append(node)

    def handle_data(self, data):
        if data and not data.isspace():  # Ignore standalone whitespace-only data
            current_node = self._peek()
            if current_node is not None:
                current_node.children.append(data)
            else:
                self.dom.append(data)


def main():
    testHTML = "<h1>Hei jeg heter <b id='whoa'>MAGNUS</b>  <br/></h1>"
    sauce = PrettySauce()
    sauce.feed(testHTML)
    pprint(sauce.dom)

    site = requests.get("http://www.pollenvarslingen.no/forsiden/Trondelag.aspx")
    bigsite = PrettySauce()
    print("Start parsing bigsite...")
    start = time.time()
    bigsite.feed(site.text)
    elapsed = time.time() - start
    print("Done parsing bigsite in {} secs".format(elapsed))
    # print(list(map(lambda e: e.type if isinstance(e, HTMLNode) else e, bigsite.dom[0].children[0].children)))
    # This is more pythonic:
    print([e.type if isinstance(e, HTMLNode) else e for e in bigsite.dom[0].children[0].children])


if __name__ == "__main__":
    main()
