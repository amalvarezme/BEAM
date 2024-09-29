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
from copy import deepcopy

from display import display

router = APIRouter()
buffer = {}

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)


display.line(
    """SSID:
DunderLab-BEAM
PASSW:
dunderlab
"""
)


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
    antenna_str = '1' if antenna else '2'
    display.line(
        f"""Bands: 88-108 MHz
SampleRate: 20 MHz
StepWidth: 20 MHz
Antenna: {antenna_str}
    """
    )
    return {
        'done': 'ok',
        'antenna': antenna_str,
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

    antenna = GPIO.input(14)
    antenna_str = '1' if antenna else '2'

    ranges = " ".join([f"{start}-{end}" for start, end in bands])

    display.line(
        f"""Bands: {ranges} MHz
SampleRate: {int(sample_rate/1e6)} MHz
StepWidth: {int(step_width/1e6)} MHz
Antenna: {antenna_str}
    """
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
    buffer_copy = deepcopy(buffer)

    if buffer_copy:
        if 'data_freqs' in buffer_copy:
            buffer_copy.pop('data_freqs')

        bands = buffer_copy['sweep_config']['bands']
        ranges = " ".join([f"{start}-{end}" for start, end in bands])

        display.line(
            f"""Bands: {ranges} MHz
SampleRate: {int(buffer_copy['sweep_config']['sample_rate']/1e6)} MHz
StepWidth: {int(buffer_copy['sweep_config']['step_width']/1e6)} MHz
Antenna: {buffer_copy['antenna']}
"""
        )

        return buffer_copy
    else:
        return {}
