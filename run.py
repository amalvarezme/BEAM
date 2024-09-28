from foundation.utils import Workers, HostWorker
from foundation.workers import LazyWorkers
import argparse

parser = argparse.ArgumentParser(description="Start an HCI worker.")
parser.add_argument(
    '-a', '--advertise_addr', default=None, help="Advertise address."
)
args = parser.parse_args()

requirements = ['chaski-confluent==0.1a5']


# ----------------------------------------------------------------------
def main():
    """"""
    workers = Workers(swarm_advertise_addr=args.advertise_addr)
    workers.stop_all_workers()

    host_workers = HostWorker(
        env='/home/user/python311/bin/python3',
    )

    workers.start_worker(
        'chaski_root',
        service_name='chaski_root',
        restart=True,
        port=51110,
        tag='1.2',
        requirements=requirements,
    )

    workers.start_worker(
        'workers/produser',
        service_name='acquisition_producer',
        restart=True,
        tag='1.2',
        requirements=requirements,
    )

    workers.start_worker(
        'workers/rt_dsp',
        service_name='rt_dsp',
        restart=True,
        tag='1.2',
        port=51150,
        requirements=requirements,
    )

    workers.swarm.start_jupyterlab(
        restart=True,
        volume_name='beam-jupyterlab',
        tag='1.2',
        requirements=requirements,
    )

    host_workers.start_worker(
        'host_workers/acquisition',
        service_name='acquisition',
        restart=True,
    )


if __name__ == '__main__':
    main()
