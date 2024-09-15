from foundation.utils import Workers
from foundation.workers import LazyWorkers
import argparse
from utils import start_service

parser = argparse.ArgumentParser(description="Start an HCI worker.")
parser.add_argument(
    '-a', '--advertise_addr', default=None, help="Advertise address."
)
args = parser.parse_args()


# ----------------------------------------------------------------------
def main():
    """"""
    workers = Workers(swarm_advertise_addr=args.advertise_addr)
    workers.stop_all_workers()
    # lazy_workers = LazyWorkers(workers)

    # Basic services
    # workers.swarm.start_ntp(restart=True)
    workers.swarm.start_jupyterlab(
        restart=True,
        volume_name='beam-jupyterlab',
        tag='1.2',
    )

    start_service('services/acquisition')


if __name__ == '__main__':
    main()
