from bs4 import BeautifulSoup, Tag
from collections import Counter
from typing import List, Optional


def find_lowest_common_ancestor(node1, node2):
    """
    Find the lowest common ancestor of two nodes in a tree.
    """
    path1 = []
    current = node1
    while current is not None:
        path1.append(id(current))
        current = current.parent

    path2 = []
    current = node2
    while current is not None:
        path2.append(current)
        current = current.parent

    path1_set = set(path1)

    for node in path2:
        if id(node) in path1_set:
            return node

    return None


def count_tags_in_soup(soup: BeautifulSoup) -> Counter:
    """
    Count the occurrences of each attribute in the entire soup.
    """
    tag_counts = Counter()

    def count_tags(element):
        if element.name and element.name not in ["script", "style"]:
            attrs = get_attr_list(element)
            tag_counts.update(attrs)
            for child in element.children:
                if isinstance(child, Tag):
                    count_tags(child)

    count_tags(soup)
    return tag_counts


def find_elements_with_text(soup: BeautifulSoup, text: str) -> List[Tag]:
    """
    Find all non-script and non-style elements that contain the given text.
    """
    output = [
        (element, id(element))
        for element in soup.find_all(
            string=lambda string: string and text.lower() in string.lower()
        )
        if element.parent.name not in ["script", "style"]
    ]

    return output


def identify_list_attribute(html: str, list_element_candidates: List[str]) -> str:
    """
    Identify the attribute with the highest ratio of appearances as lowest common ancestor
    to total appearances in the HTML.

    Args:
    html (str): The HTML content as a string
    list_element_candidates (List[str]): A list of text snippets that are likely to be list elements

    Returns:
    str: The attribute with the highest ratio
    """
    soup = BeautifulSoup(html, "html.parser")

    element_candidates = []
    for identifier in list_element_candidates:
        elements = find_elements_with_text(soup, identifier)
        if elements:
            element_candidates += elements

    element_candidates = list(set(element_candidates))

    possible_attrs = []
    for el1, _ in element_candidates:
        for el2, _ in element_candidates:
            common_ancestor = find_lowest_common_ancestor(el1, el2)
            if isinstance(common_ancestor, Tag):
                possible_attrs += get_attr_list(common_ancestor)

    attr_counts = Counter(possible_attrs)
    total_tags = count_tags_in_soup(soup)

    normalized_counts = {}
    for attr, count in attr_counts.items():
        if total_tags[attr] > 0:
            normalized_counts[attr] = count / total_tags[attr]

    print("normalized_counts of attribute candidates:", normalized_counts)

    if normalized_counts:
        return max(normalized_counts, key=normalized_counts.get)
    else:
        return None


# TODO: consolidate into a single function


def get_attr_list(element, ignore_num=True):
    """
    Get all attributes from an element.
    """

    attribute_values = list(element.attrs.values())

    attr_lst = []
    attr_lst.append(element.name)

    for value in attribute_values:
        if ignore_num:
            try:
                int(value)
                continue
            except (ValueError, TypeError):
                pass

        if isinstance(value, list):
            attr_lst += value
        else:
            attr_lst.append(value)

    return attr_lst


def get_attr_keys(element: Tag, ignore_num=True) -> List[str]:
    """Get list of attribute keys from an element and its parents"""

    attr_keys = list(element.attrs.keys())

    attr_lst = []
    attr_lst.append(element.name)

    for key in attr_keys:
        if ignore_num:
            try:
                int(key)
                continue
            except (ValueError, TypeError):
                pass
        
        if isinstance(key, list):
            attr_lst += key
        else:
            attr_lst.append(key)

    return attr_lst


def get_attr_values(element: Tag, ignore_num=True) -> List[str]:
    """Get list of attribute values from an element and its parents"""
    attr_values = list(element.attrs.values())

    attr_lst = []
    attr_lst.append(element.name)

    for value in attr_values:
        if ignore_num:
            try:
                int(value)
                continue
            except (ValueError, TypeError):
                pass
        
        if isinstance(value, list):
            attr_lst += value
        else:
            attr_lst.append(value)

    return attr_lst