import json
import os
import asyncio
from pymongo.asynchronous.collection import AsyncCollection
from models.build import BuildOutput
from models.context import Context
from pymongo import AsyncMongoClient
from conf import config, logger
import aiofiles


def save_builder_output(context: Context, output: BuildOutput):
    try:
        if not os.path.exists("logs/usage"):
            os.makedirs("logs/usage", exist_ok=True)

        with open(f"logs/usage/{context.logger_context.chat_id}.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "context": context.to_json(),
                        "output": output.model_dump(),
                    }
                )
                + "\n"
            )
    except Exception as e:
        context.logger_context.logger.error(f"Error saving builder output: {e}")


async def load_usages_async(collection: AsyncCollection, file_path: str):
    global logger
    try:
        async with aiofiles.open(file_path, "r") as f:
            for line in await f.readlines():
                usage = json.loads(line)
                request_id = usage["context"]["request_id"]
                # check if request_id is already in the database
                if await collection.find_one({"context.request_id": request_id}):
                    continue
                else:
                    await collection.insert_one(usage)

    except Exception as e:
        logger.error(f"Error loading usages: {e}")


async def upload_usages_async() -> None:
    try:
        client = AsyncMongoClient(config.mongo.mongo_uri)  # pyright: ignore[reportOptionalMemberAccess]
        collection: AsyncCollection = client.get_database(
            config.mongo.database_name  # pyright: ignore[reportOptionalMemberAccess]
        ).get_collection(config.mongo.collection_name)  # pyright: ignore[reportOptionalMemberAccess]
        tasks = []
        for file in os.listdir("logs/usage"):
            tasks.append(load_usages_async(collection, f"logs/usage/{file}"))

        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error uploading usages: {e}")
    finally:
        await client.close()
