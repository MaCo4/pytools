from pprint import pprint


if __name__ == "__main__":
    parser = LDIFParser(open('C:\\Users\Magnus\Desktop\ipa\ipa-data-2017-08-24-01-00-07\TIHLDE-ORG-userRoot.ldif', 'rb'))
    for dn, entry in parser.parse():
        if dn is not None and "magnushy" in dn.lower():
            print("DN: {}".format(dn))
            pprint(entry)
