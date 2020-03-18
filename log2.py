#!/usr/bin/python
#
# Poll and log data collected from one or more MCC118 ADC boards
# See also the `daqhats_read_eeproms` and `daqhats_list_boards` command line
# tools

# pull in python standard library functions
import os
import sys
from time import gmtime, sleep, strftime, time

# pull in the daqhat library
from daqhats import hat_list, HatIDs, mcc118


class DAQDataLogger:
    '''
    Scan the inputs on one or more MCC 118 boards and log data to a file
    in a loop (unitl interrupted) using the log method.
    '''

    def __init__(self):
        '''
        Detect boards and get ready to be interrupted
        '''
        self.running = False

        # get hat list of MCC daqhat boards
        self.boards = hat_list(filter_by_id = HatIDs.MCC_118)
        self.boardsEntry = []
        for entry in self.boards:
            self.boardsEntry.append( mcc118(entry.address) )
        if not self.boards:
            sys.stderr.write("No boards found\n")
            sys.exit()


    def handle_interupt(self, signum, frame):
        '''
        Signal handler that ends a call to log
        '''
        self.running = False


    def log(self, outfile):
        '''
        In a loop (until interrupted) scan the inputs of all detected boards
        and output data to a tab delimited text file with a single header row
        '''
        data = ["time"]
        for entry in self.boards:
            board = mcc118(entry.address)
            for channel in range(board.info().NUM_AI_CHANNELS):
                # Build channel label
                data.append("{}.{}".format(entry.address, channel))
        # DEBUG
        #print(self.boards)
        line = "\t".join(data)
        outfile.write(line)
        outfile.write("\n")
        
        tmpCounter = 0
        self.running = True
        while self.running:
            now = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()))
            data = [now]
            # Read and display every channel
            #for entry in self.boards:
            for board in self.boardsEntry:
                if tmpCounter == 71 and entry.address == 6:
                    print("*"*4)
                    print("Here it comes!")
                    print("*"*4)
                #board = mcc118(entry.address)
                for channel in range(board.info().NUM_AI_CHANNELS):
                    #data.append(str(board.a_in_read(channel)))
                    data.append("%.4f" % board.a_in_read(channel) )

            line = "\t".join(data)
            outfile.write(line)
            outfile.write("\n")
            sleep(0.5)
            tmpCounter += 1
            print("Iteration #%d" % tmpCounter)
        outfile.close() 


# Main program starts here. Use `python3 log2.py` to run
# check prevents running of program if loading (import) as a module
if __name__ == "__main__":
    # Pull in python standard libraries only used when running as program
    import argparse
    import signal

    # Look at Command Line
    parser = argparse.ArgumentParser(
        description='Poll and log data collected from one or more MCC118 ADC boards',
        epilog='See also the `daqhats_read_eeproms` and `daqhats_list_boards`')
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
        default=sys.stdout, help='File to which log data')
    args = parser.parse_args()

    # Create Data Logger
    logger = DAQDataLogger()

    # Add signal handler so systemd can shutdown service
    signal.signal(signal.SIGINT, logger.handle_interupt)
    signal.signal(signal.SIGTERM, logger.handle_interupt)

    logger.log(args.outfile)
