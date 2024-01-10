import os
import lxml.etree as ET
import requests
import json
from tqdm import tqdm
from config import NAMESPACES, XPATHS

namespaces = NAMESPACES
label_x = XPATHS["label"]
comment_x = XPATHS["comment"]
restriction_properties_x = XPATHS["restriction_properties"]
restriction_cardinality_x = XPATHS["restriction_cardinality"]


def parse_rdf_xml(url) -> ET.ElementTree:
    """Parse RDF/XML file and return the root element"""
    for prefix, uri in tqdm(namespaces.items(), total=len(namespaces)):
        ET.register_namespace(prefix, uri)
    p = ET.XMLParser(huge_tree=True)
    response = requests.get(url)
    tree = ET.fromstring(response.content, parser=p)
    print("tree parsed")
    return tree


def save_rdf_xml(root: ET.ElementTree, path) -> None:
    """Save RDF/XML file"""
    os.makedirs("out", exist_ok=True)
    with open(os.path.join("out", f"{path}.xml"), "wb") as f:
        f.write(ET.tostring(root, pretty_print=True))
    print(f"{path}.xml saved")


def get_label_and_comment(element: ET.Element) -> tuple[str, str]:
    """Return the label and comment of a given element"""
    try:
        label = element.xpath(label_x,
                              namespaces=namespaces)[0]
    except IndexError:
        label = ""
    try:
        comment = element.xpath(comment_x,
                                namespaces=namespaces)[0]
    except IndexError:
        comment = ""
    return label, comment


def get_elements(root: ET.ElementTree, xpath) -> list:
    """Return a list of etree elements of a given xpath and root"""
    elements = root.xpath(xpath, namespaces=namespaces)
    return elements


def save_dict(input, path) -> None:
    """saving all dictionaries to json files"""
    os.makedirs("out", exist_ok=True)
    with open(os.path.join("out", f"{path}.json"), "w") as f:
        json.dump(dict(sorted(input.items())), f, indent=2)
    print(f"{path}.json saved")


def create_baserow_json(input: list) -> tuple[dict, dict]:
    """Create a dictionary of object properties"""
    baserow_dict = {}
    baserow_dict_id = {}
    num = 1
    for x in tqdm(input, total=len(input)):
        label, comment = get_label_and_comment(x)
        about = x.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"]
        if "#" in about:
            about_key = about.split("#")[-1]
            ns = f'{about.split("#")[0]}#'
        else:
            about_key = about.split("/")[-1]
            ns = about.replace(about_key, "")
        try:
            baserow_dict_id[about]
        except KeyError:
            baserow_dict_id[about] = num
            num += 1
        dict_id = baserow_dict_id[about]
        baserow_dict[dict_id] = {
            "id": dict_id,
            "order": f"{ dict_id }.00000000000000000000",
            "Name": about_key,
            "Namespace": ns,
            "Label": label,
            "Notes": comment
        }
    return baserow_dict, baserow_dict_id


def extend_baserow_json(
    input: dict,
    input_ids: dict,
    schema: ET.ElementTree
) -> dict:
    """create extended baserow json files of classes, object properties and datatype properties"""
    for x in tqdm(input, total=len(input)):
        c_dict_id = input[x]["id"]
        x_name = f"{input[x]['Namespace']}{input[x]['Name']}"
        xpath_id = f"//rdfs:subClassOf[child::owl:Restriction and parent::owl:Class[@rdf:about='{x_name}']]"
        extend = get_elements(schema, xpath_id)
        extendedMin = []
        extendedMax = []
        for x in tqdm(extend, total=len(extend)):
            onProperty, cardinality = get_elements(x, restriction_properties_x), \
                get_elements(x, restriction_cardinality_x)
            for prop, card in zip(onProperty, cardinality):
                p = prop.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
                c_datatype = card.tag.split("}")[-1]
                try:
                    ipid2 = input_ids[p]
                    if c_datatype == "minCardinality":
                        extendedMin.append(ipid2)
                    elif c_datatype == "maxCardinality":
                        extendedMax.append(ipid2)
                except KeyError:
                    print("KeyError: not found in input_ids")
        input[c_dict_id]["Min1"] = extendedMin
        input[c_dict_id]["Max1"] = extendedMax
    return input


def extend_baserow_json2(
    input: dict,
    input_ids: dict,
    column: str,
    xpath: str = False,
    xpath2: str = False,
    schema: ET.ElementTree = False
) -> dict:
    """create extended baserow json files of classes, object properties and datatype properties"""
    for x in tqdm(input, total=len(input)):
        c_dict_id = input[x]["id"]
        x_name = f"{input[x]['Namespace']}{input[x]['Name']}"
        xpath_id = f"//rdfs:{xpath}[not(child::owl:Restriction) and parent::owl:{xpath2}[@rdf:about='{x_name}']]"
        extend = get_elements(schema, xpath_id)
        extended = []
        extendedNonLinked = []
        for x in tqdm(extend, total=len(extend)):
            try:
                s_resource = x.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"]
                try:
                    c_id = input_ids[s_resource]
                    extended.append(c_id)
                except KeyError:
                    extendedNonLinked.append(s_resource)
            except KeyError:
                print("IndexError: not found in input_ids")
                print(x)
                print(xpath_id)
        try:
            for x in extended:
                input[c_dict_id][column].append(x)
            input[c_dict_id][f"{column}_NonLinked"] += " ".join(extendedNonLinked)
        except KeyError:
            input[c_dict_id][column] = extended
            input[c_dict_id][f"{column}_NonLinked"] = " ".join(extendedNonLinked)
    return input
