from foundation.radiant.utils import environ
from figurestream import FigureStream
from chaski.streamer import ChaskiStreamer
from dunderlab.api import aioAPI as API
import time
import numpy as np
import asyncio
from scipy.signal import welch
import logging


########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.axis = self.add_subplot(111)
        # self.x = np.array(range(100))
        # self.t0 = time.time()
        # self.y = [self.t0] * 100

        # self.axis.set_title('FigureStream')
        # self.axis.set_xlabel('Frquency [MHz]')
        # self.axis.set_ylabel('Power Spectral Density (V²/Hz)')

        # self.line1, *_ = self.axis.plot(
        # [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # )

    # ----------------------------------------------------------------------
    async def init_chaski(self):
        """"""
        self.consumer = ChaskiStreamer(
            name='Acquisition Consumer',
            root=False,
            paired=True,
            run=True,
            subscriptions=['raw'],
        )
        await self.consumer.connect('chaski-root-worker', 51110)
        logging.warning('Connected.')

    # ----------------------------------------------------------------------
    async def stream(self):
        """"""
        await self.init_chaski()

        history = {}

        logging.warning('Waiting for data...')
        async with self.consumer as message_queue:
            async for incoming_message in message_queue:
                self.axis.clear()
                logging.warning('Ploting...')

                data = incoming_message.data

                sweep_config = data['sweep_config']
                data_freqs = data['data_freqs']

                for i, f in enumerate(data_freqs):

                    signal = data_freqs[f]
                    w, x = welch(
                        signal,
                        fs=sweep_config['sample_rate'],
                        nperseg=256,
                        scaling='spectrum',
                        return_onesided=False,
                    )

                    sorted_indices = np.argsort(w)
                    w_sorted = (
                        w[sorted_indices] + f + sweep_config['step_offset']
                    )
                    x_sorted = x[sorted_indices]
                    x_sorted = 10 * np.log10(x_sorted)

                    history.setdefault(f, []).append(x_sorted)
                    if len(history[f]) > 20:
                        history[f] = history[f][-20:]

                    for j, h in enumerate(history[f][::1]):

                        self.axis.plot(
                            w_sorted / 1e6 + (j * 0.5),
                            h + (j * 15),
                            color=f'C{i}',
                            zorder=100 - j,
                            linewidth=3,
                        )
                        self.axis.fill_between(
                            w_sorted / 1e6 + (j * 0.5),
                            -120,
                            h + (j * 15),
                            color='w',
                            zorder=100 - j,
                        )

                self.axis.set_xlabel("Frequency (MHz)")
                self.axis.set_ylabel("Power Spectral Density (dB)")
                # self.axis.gca().spines['top'].set_visible(False)
                # self.axis.gca().spines['right'].set_visible(False)

                # self.axis.set_ylim(-1e-9, 15e-9)

                self.feed()
                logging.warning('Feeding...')


if __name__ == '__main__':
    figure_stream = Stream(host='0.0.0.0', port=environ('PORT', '5001'))
    asyncio.run(figure_stream.stream())
