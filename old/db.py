from fastapi import FastAPI
import uvicorn

from dunderlab.api import aioAPI as API


app = FastAPI()

# ----------------------------------------------------------------------
@app.get('/')
def test():
    """"""
    return {'ok': True,}



# ----------------------------------------------------------------------
@app.get('/initialize/')
async def initialize():
    """"""
    TOKEN = {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NjY4Mzg5OCwiaWF0IjoxNzI1MTQ3ODk4LCJqdGkiOiIzMTFlNDlmYWYxOGY0MTNmOGUyYjkzYzA1M2M2NGE5YyIsInVzZXJfaWQiOjF9.PDcOG9Y-bYEWDz6i9B02tORsM69RLIF3nj4wFBMjxR0",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1MjM0Mjk4LCJpYXQiOjE3MjUxNDc4OTgsImp0aSI6ImU4MTQwMDA4NjJkOTQ4MzFhNWUwYTkyOGJhNjJmY2U5IiwidXNlcl9pZCI6MX0.dzlH-ZiUiaInER6Qale70BRb5N37RVN01szokgqRLmM"
    }
    api = API('http://127.0.0.1:51102/timescaledbapp/', token=TOKEN["access"])

    await api.source.post({
        'label': 'sdr',
        'name': 'HackRF One',
        'location': 'None',
        'device': 'None',
        'protocol': 'None',
        'version': '0.1',
        'description': 'BEAM: Broad Electromagnetic Activity Monitoring',
    })

    await api.measure.post({
        'source': 'sdr',
        'label': 'ant500',
        'name': 'ANT500',
        'description': 'Raw signal from ANT500 Antenna',
    })

    await api.measure.post({
        'source': 'sdr',
        'label': 'taoglas',
        'name': 'Taoglas TG.66.A113',
        'description': 'Raw signal from Taoglas Antenna',
    })

    channels_names = ['I','Q']

    await api.channel.post([{
        'source': 'sdr',
        'measure': 'antt500',
        'name': channel,
        'label': channel,
        'unit': 'None',
        'sampling_rate': '1',
    } for channel in channels_names])

    await api.channel.post([{
        'source': 'sdr',
        'measure': 'taoglas',
        'name': channel,
        'label': channel,
        'unit': 'None',
        'sampling_rate': '1',
    } for channel in channels_names])

    return {'done': 'ok'}




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=51190)
