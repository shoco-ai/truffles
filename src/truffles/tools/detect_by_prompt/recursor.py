import asyncio
from enum import Enum

from truffles.tools.detect_by_prompt.messages import get_prompt

THRESHOLD = 2000


class Result(Enum):
    FOUND = "found"
    PARTIAL = "partial"
    NOT_FOUND = "not_found"


async def traverse(node, model, prompt):
    id_list = []
    llm_calls = []

    async def _impl(node, depth=0):
        if "text" not in node["properties"].keys() or len(node["properties"]["text"]) > THRESHOLD:
            if len(node["children"]) == 0:
                return Result.NOT_FOUND

            out = []
            for c in node["children"]:
                out.append(_impl(c, depth + 1))
            await asyncio.gather(*out)

            if Result.PARTIAL in out:
                return Result.PARTIAL
            elif Result.FOUND in out:
                return Result.FOUND
            else:
                return Result.NOT_FOUND

        else:
            # print("calling at depth", depth, "by node with id", node["id"])
            # print("prompt: ", get_prompt(node, prompt))
            # print("node: ", node)
            result = await model.ainvoke(get_prompt(node, prompt))
            llm_calls.append(result)
            # print("result: ", result)
            # print("locator list so far: ", id_list)
            # print("-" * 30)

            if result.match == "partial":
                out = []
                for c in node["children"]:
                    out.append(_impl(c, depth + 1))
                await asyncio.gather(*out)
                return Result.PARTIAL

            elif result.match == "found":
                id_list.append(node["id"])
                return Result.FOUND
            else:
                return Result.NOT_FOUND

    await _impl(node, 0)

    return id_list
