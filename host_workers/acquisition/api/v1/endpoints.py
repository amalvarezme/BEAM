from fastapi import APIRouter, Body
from hackrf import ScanHackRF

from contextlib import asynccontextmanager
from typing import Optional

import asyncio
import json
import numpy as np
import gpsd2
import time
import RPi.GPIO as GPIO


router = APIRouter()
buffer = {}


GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)


# ----------------------------------------------------------------------
def get_gps():
    """"""
    try:
        packet = gpsd2.get_current()
        lat, long = packet.position()
        return {
            'latitude': lat,
            'longitude': long,
        }
    except:
        gpsd2.connect()
        time.sleep(1)
        return get_gps()


# ----------------------------------------------------------------------
def custom_callback(data_freqs, sweep_config):
    """"""
    global buffer

    antenna = GPIO.input(14)

    buffer = {
        'sweep_config': sweep_config,
        'gps': get_gps(),
        'antenna': '1' if antenna else '2',
        'data_freqs': data_freqs,
    }


# ----------------------------------------------------------------------
def serialize(buffer):
    data = buffer['data_freqs']
    for freq in data:
        data[freq] = {
            'P': np.array(data[freq]).real.tolist(),
            'Q': np.array(data[freq]).imag.tolist(),
        }

    return buffer


# ----------------------------------------------------------------------
@router.get('/')
async def initialice():
    global scanhackrf

    try:
        scanhackrf.stop_rx()
    except:
        scanhackrf = ScanHackRF(0)

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

    antenna = GPIO.input(14)
    return {
        'done': 'ok',
        'antenna': '1' if antenna else '2',
    }


# ----------------------------------------------------------------------
@router.put('/acquisition/')
async def acquisition(
    bands: list[tuple[int, int]] = Body(...),
    sample_rate: float = Body(...),
    step_width: float = Body(...),
    read_num_blocks: int = Body(...),
    buffer_num_blocks: int = Body(...),
    step_offset: Optional[float] = Body(None),
    antenna: Optional[int] = Body(1),
):
    global scanhackrf

    try:
        scanhackrf.stop_rx()
    except:
        scanhackrf = ScanHackRF(0)

    status = {}
    match antenna:
        case 1:
            GPIO.output(14, GPIO.HIGH)
            status['antenna'] = 1
        case 2:
            GPIO.output(14, GPIO.LOW)
            status['antenna'] = 2
        case _:
            status['antenna'] = (
                f'Invalid antenna selection: {antenna}. Please choose either 1 or 2.'
            )

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
    return {'done': 'ok', **status}


# ----------------------------------------------------------------------
@router.get('/acquisition/')
async def get_buffer():
    """"""
    if buffer:
        return serialize(buffer)
    else:
        return {}


# ----------------------------------------------------------------------
@router.get('/status/')
async def get_status():
    """"""
    if buffer:
        if 'data_freqs' in buffer:
            buffer.pop('data_freqs')
        return buffer
    else:
        return {}
