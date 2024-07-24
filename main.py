import json

import websockets
import asyncio
from datetime import datetime
from matplotlib import pyplot
import numpy as np

time_diff = [[], [], [], [], []]

SOCKETS_AMOUNT = 5
DATA_TIMER = 1


async def handler():
    # await asyncio.wait([handle_socket(target) for target in connections])
    tasks = [asyncio.Task(handle_socket(target)) for target in connections]
    await asyncio.sleep(DATA_TIMER)
    for task in tasks:
        task.cancel()


async def handle_socket(target):
    async with websockets.connect(target["uri"]) as websocket:
        async for message in websocket:
            message_json = json.loads(message)
            now = datetime.utcnow().timestamp() * 1e3
            tz_correction = 8 * (60 ** 2) * 1e3
            diff = now - (message_json["data"]["E"] - tz_correction)
            if diff != 0:
                time_diff[target["id"]].append(abs(diff))
            # print(target["id"], message_json)


def stats(values):
    values = np.array(values, dtype=float)
    counts, bins = np.histogram(values)
    mids = 0.5 * (bins[1:] + bins[:-1])
    probs = counts / np.sum(counts)
    mean = np.sum(probs * mids)
    sd = np.sqrt(np.sum(probs * (mids - mean) ** 2))
    return mean, sd


if __name__ == "__main__":
    connections = []
    for i in range(SOCKETS_AMOUNT):
        connections.append({"id": i, "uri": "wss://fstream.binance.com/stream?streams=btcusdt@bookTicker"})
    asyncio.get_event_loop().run_until_complete(handler())
    for i in range(SOCKETS_AMOUNT):
        pyplot.hist(time_diff[i], density=True, histtype='step', bins=100, cumulative=-1,
                    label="Connection {0}".format(i))
        expected_value, standard_deviation = stats(time_diff[i])
        print("Standard deviation for {0} connection: {1}"
              .format(i, standard_deviation))
        print("Expected value for {0} connection: {1}"
              .format(i, expected_value))
    pyplot.legend(loc='lower left')
    pyplot.grid(True)
    pyplot.show()
