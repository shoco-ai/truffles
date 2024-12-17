import os
from collections import Counter

from playwright.async_api import Page

from truffles import TRUFFLES_ATTRIBUTE_ID


def get_node_text(node, separator="] ["):
    if len(node["children"]) == 0:
        return node["properties"].get("text", "")
    else:
        return "[ " + separator.join([get_node_text(child, separator) for child in node["children"]]) + " ]"


def count_children(json_obj):
    counter = Counter()

    def _impl(json_obj):
        # Base case: if not a dict or list, return
        if not isinstance(json_obj, (dict, list)):
            return

        counter[len(json_obj["children"])] += 1
        for child in json_obj["children"]:
            _impl(child)

    _impl(json_obj)
    return counter


def prune_tree(json_obj):
    if len(json_obj["children"]) == 0:  # leaf case
        if json_obj["properties"].get("text", "") == "":
            return None
        else:
            return json_obj
    else:  # non-leaf case
        if len(json_obj["children"]) == 1:
            return prune_tree(json_obj["children"][0])
        else:
            new_children = [prune_tree(child) for child in json_obj["children"]]
            json_obj["children"] = [child for child in new_children if child is not None]
            return json_obj


async def generate_ax_tree(page: Page, prune: bool = True) -> str:
    # Read the JavaScript file content
    js_file_path = os.path.join(os.path.dirname(__file__), "ax_tree_generate.js")
    with open(js_file_path, "r") as file:
        js_code = file.read()

    # Evaluate the JavaScript code and call the function
    ax_tree = await page.evaluate(
        f"""() => {{
        {js_code}
        return generateAccessibilityTree("{TRUFFLES_ATTRIBUTE_ID}");
        }}"""
    )

    if prune:
        ax_tree = prune_tree(ax_tree)

    return ax_tree
