from chaski.streamer import ChaskiStreamer
from dunderlab.api import aioAPI as API
import asyncio
import numpy as np


# ----------------------------------------------------------------------
async def run():
    """"""
    api = API('http://host.docker.eth0:51190/')
    streamer = ChaskiStreamer(
        name='Acquisition Produser',
        root=False,
        paired=True,
        run=True,
    )
    await streamer.connect('chaski-root-worker', 51110)

    while True:

        response = await api.acquisition.get()

        if not response:
            #             await asyncio.sleep(0.1)
            continue

        data = {
            'sweep_config': response['sweep_config'],
            'data_freqs': {
                int(f): np.array(response['data_freqs'][f]['P'])
                + np.array(response['data_freqs'][f]['Q']) * 1j
                for f in response['data_freqs']
            },
        }

        await streamer.push('raw', data)
        await asyncio.sleep(1)


# ----------------------------------------------------------------------
def main():
    """"""
    asyncio.run(run())


if __name__ == '__main__':
    main()
