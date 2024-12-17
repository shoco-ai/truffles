import asyncio
from enum import Enum

from truffles.tools.detect_by_prompt.messages import get_prompt
from truffles.utils.ax_tree.generate import get_node_text

THRESHOLD = 2000


class Result(Enum):
    EXACT_MATCH = "exact_match"
    TOO_MANY = "too_many"
    NOT_FOUND = "not_found"


async def traverse(node, model, prompt):
    id_list = []
    llm_calls = []

    async def _impl(node, depth=0):
        if len(get_node_text(node)) > THRESHOLD:
            if len(node["children"]) == 0:
                return Result.NOT_FOUND

            out = []
            for c in node["children"]:
                out.append(_impl(c, depth + 1))
            await asyncio.gather(*out)

            if Result.TOO_MANY in out:
                return Result.TOO_MANY
            elif Result.EXACT_MATCH in out:
                return Result.EXACT_MATCH
            else:
                return Result.NOT_FOUND

        else:
            if len(llm_calls) > 50:
                raise Exception("Too many LLM calls")

            result = await model.ainvoke(get_prompt(node, prompt))
            llm_calls.append(result)

            if result.match == "too_many":
                out = []
                for c in node["children"]:
                    out.append(_impl(c, depth + 1))
                await asyncio.gather(*out)
                return Result.TOO_MANY

            elif result.match == "exact_match":
                id_list.append(node["id"])
                return Result.EXACT_MATCH

            elif result.match == "not_found":
                return Result.NOT_FOUND
            else:
                print("GOT MYSTERIOUS RESPONSE: ", result)

    await _impl(node, 0)

    return id_list
