import os
import node
import threading
import requests
import time
from miner import Miner


if __name__ == '__main__':
    miners = []
    blocks_to_update = 5
    time_per_block = 10

    while True:
        hashrate = input('Type a number to create a miner with the given hashrate: ')
        try:
            # Check if user input is an integer
            hashrate = int(hashrate)
        except ValueError:
            print('INPUT ERROR: Hashrate must be an integer')
            # Go back to the start of the while loop if invalid input
            continue

        if hashrate > 0:
            # If user inputs a positive hashrate, create a new miner with the given hashrate
            miner = Miner(5000+len(miners),hashrate,miners,blocks_to_update,time_per_block)
            miners.append(miner)
            print('MINER {} ADDED'.format(len(miners)-1))
        elif hashrate == 0:
            # If user inputs a zero, pause the last miner in the list
            miners[-1].stop_mining()
            # User can press enter to make the last miner resume mining
            input('Miner {} Stopped Mining, Press Enter to resume: '.format(len(miners)-1))
            miners[-1].start_mining()
        else:
            # If user inputs a negative integer, break out of the while loop
            break
    #END OF WHILE LOOP


    # Start shutting down all miner nodes
    for miner in miners:
        miner.shutdown_node()
    # Wait for each mining thread to end
    for miner in miners:
        miner.mining_thread.join()