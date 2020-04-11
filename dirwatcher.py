#! usr/bin/env python

import logging
import datetime
import time
import argparse
import os
import signal

__author__ = '''Patrick Buzzo (Assistance from Piero/David Stewy Videos,
                Mike/Piero Dirwatcher walkthrough
            '''

logger = logging.getLogger(__file__)
# Directory of files that will be systematically searched for the magic text
watching_files = {}
exit_flag = False


def signal_handler(sig, frame):
    """
    When SIGINT or SIGTERM is provided, this function will
    alter global exit flag variable to cause an exit
    """
    logger.info('Signal Received By Program: ' + signal.Signals(sig).name)
    global exit_flag
    if sig == signal.SIGINT or signal.SIGTERM:
        logger.info('Shutting Down Dirwatcher Program...')

        # Will cause termination of program, when changed to true,
        # the program terminates
        exit_flag = True


def read_file(file, starting_spot, magic_word):
    """
    This function will read through the provided file,
    beginning from the 'starting_point', and will check for the magic
    text.
    """
    line_number = 0
    with open(file) as f:
        for line_number, line in enumerate(f):
            if line_number >= starting_spot:
                if magic_word in line:
                    logger.info(
                        f'{file}: found "{magic_word}" on line {line_number+1}'
                    )
    new_spot = line_number + 1
    return new_spot


def watch_dir(args):
    file_list = os.listdir(args.path)

    for f in file_list:
        if f.endswith(args.ext) and f not in watching_files:
            watching_files[f] = 0
            logger.info(f'{f} is now being monitiored.')
    for f in list(watching_files):
        if f not in file_list:
            logger.info(f'{f} is no longer being monitored.')
            del watching_files[f]
    # check all files in watching_files for magic text, using read_file()
    for f in watching_files:
        watching_files[f] = read_file(
            os.path.join(args.path, f),
            watching_files[f],
            args.magic
        )


def create_parser():
    """
    Create parser to parse command line arguments supplied by user
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--ext', type=str, default='.txt',
                        help='Text file extension to watch')
    parser.add_argument('-i', '--interval', type=float, default=1.0,
                        help='Number of seconds between polling')
    parser.add_argument('path', help='Directory to watch')
    parser.add_argument('magic', help='String to watch')
    return parser


def main():
    # connect logger with console output, ref Piero walkthrough
    logging.basicConfig(
        filename='dirwatcher.log',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s [%(threadName)-12s] %(message)s',
        datefmt='%Y-%m--%d %H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)
    # Timestamp
    app_start_time = datetime.datetime.now()
    # Start banner
    logger.info(
        '\n'
        '---------------------------------------------------------------\n'
        '    Running {0}\n'
        '    Started on {1}\n'
        '---------------------------------------------------------------\n'
        .format(__file__, app_start_time.isoformat())
    )
    # Parse command-line arguments to be used
    parser = create_parser()
    args = parser.parse_args()

    # Watch for SIGINT or SIGTERM during running of program
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not exit_flag:
        try:
            watch_dir(args)
        except OSError:
            logger.error('This directory does not exist')
            time.sleep(5)
        except Exception as e:
            logger.error('Unhandled exception: {}'.format(e))
        # execute watch_dirs() every [args.interval] seconds
        time.sleep(args.interval)

    # Convert uptime of program to be displayed in closing banner
    uptime = datetime.datetime.now() - app_start_time
    # Closing banner
    logger.info(
        '\n'
        '---------------------------------------------------------------\n'
        '    Stopped {0}\n'
        '    Uptime on {1}\n'
        '---------------------------------------------------------------\n'
        .format(__file__, str(uptime))
    )


if __name__ == '__main__':
    main()
