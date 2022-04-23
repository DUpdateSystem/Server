import argparse

from .nng_discovery import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b',
                        '--bind',
                        dest='bind_addr',
                        help='discovery server bind address',
                        type=str,
                        required=True)
    args = parser.parse_args()
    main(args.bind_addr)
