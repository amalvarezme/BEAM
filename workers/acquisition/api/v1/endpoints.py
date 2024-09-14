from fastapi import APIRouter, Body
from hackrf import ScanHackRF
from contextlib import asynccontextmanager
from typing import Optional
import asyncio
import json
import numpy as np

router = APIRouter()
buffer = {}


def custom_callback(data_freqs, sweep_config):
    """"""
    global buffer

    buffer = {
        'config': sweep_config,
        'data': data_freqs,
    }


def serialize(buffer):

    data = buffer['data']

    for freq in data:
        data[freq] = {
            'P': np.array(data[freq]).real.tolist(),
            'Q': np.array(data[freq]).imag.tolist(),
        }

    return buffer


# ----------------------------------------------------------------------
@router.put('/acquisition/')
async def acquisition(
    bands: list[tuple[int, int]] = Body(...),
    sample_rate: float = Body(...),
    step_width: float = Body(...),
    read_num_blocks: int = Body(...),
    buffer_num_blocks: int = Body(...),
    step_offset: Optional[float] = Body(None),
):
    global scanhackrf

    try:
        scanhackrf.stop_rx()
    except:
        scanhackrf = ScanHackRF(0)

    scanhackrf.scan(
        bands=bands,
        sample_rate=sample_rate,
        step_width=step_width,
        step_offset=step_offset,
        read_num_blocks=read_num_blocks,
        buffer_num_blocks=buffer_num_blocks,
        callback=custom_callback,
        interleaved=False,
    )
    return {'done': 'ok'}


# ----------------------------------------------------------------------
@router.get('/acquisition/')
async def get_buffer():
    """"""
    if buffer:
        return serialize(buffer)
    else:
        return {}
