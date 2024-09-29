from hackrf import ScanHackRF

scanhackrf = ScanHackRF(0)


def custom_callback(data_freqs, sweep_config):
    """"""
    print('x')
    data_freqs


scanhackrf.scan(
    bands=[
        (88, 108),
    ],
    sample_rate=20e6,
    step_width=20e6,
    step_offset=None,
    read_num_blocks=1,
    buffer_num_blocks=1,
    callback=custom_callback,
    interleaved=False,
)
