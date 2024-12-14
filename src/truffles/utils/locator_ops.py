import copy
from typing import List

from playwright.async_api import Locator


def combine_locator_list(locators: List[Locator]) -> Locator:
    """Combines a list of locators into a single locator to increase usability.
    The original locators can be retrieved with .all()"""

    locators = copy.copy(locators)

    combined_loc = locators[0]
    for locator in locators[1:]:
        combined_loc = combined_loc.or_(locator)

    return combined_loc
