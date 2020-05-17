import os
import requests
import threading

class Miner:
    def __init__(self, port, hash_rate=None):
        self.port = port
        self.hash_rate = hash_rate
        self.node_thread = threading.Thread(target=self.start_server)
        self.mining_thread = threading.Thread(target=self.mine)
        self.continue_mining = False
        self.setup_node()
        print('MINER CREATED: port={}  hashrate={}'.format(port, hash_rate))

    def mine(self):
        ''' Target function of self.mining_thread, it automamically mines blocks
        until it is signalled to stop '''
        self.continue_mining = True
        url = 'http://localhost:{}/mine'.format(self.port)
        while self.continue_mining == True:
            try:
                response = requests.post(url)
            except requests.exceptions.ConnectionError:
                print('MINING FAILED: Unable to connect to server ',self.port)
                self.continue_mining = False
    
    def start_mining(self):
        ''' Start the thread for automatic mining '''
        self.mining_thread.start()
    
    def stop_mining(self):
        ''' This method signals the miner to stop mining '''
        self.continue_mining = False
        url = 'http://localhost:{}/halt_mining'.format(self.port)
        try:
            response = requests.post(url)
        except requests.exceptions.ConnectionError:
            print('Unable to halt mining',self.port)
            self.continue_mining = False
        self.mining_thread.join()
        # Reset self.mining_thread
        self.mining_thread = threading.Thread(target=self.mine)
        print('Miner {} stopped mining'.format(self.port))
    
    def start_server(self):
        ''' Target function of self.node_thread, it starts up a flask server for the miner '''
        os.system("python node.py --port {} --hashrate {}".format(self.port,self.hash_rate))
    
    def setup_node(self):
        ''' Start the thread for the flask server and sets it up '''
        self.node_thread.start()
        blockchain_file = 'blockchain-{}.txt'.format(self.port)
        wallet_file = 'wallet-{}.txt'.format(self.port)

        # Delete blockchain file if it exists
        if os.path.exists(blockchain_file):
            os.remove(blockchain_file)
        
        # Delete wallet file if it exists
        if os.path.exists(wallet_file):
            os.remove(wallet_file)
        
        # Send a request to create a new wallet
        url = 'http://localhost:{}/wallet'.format(self.port)
        try:
            response = requests.post(url)
        except requests.exceptions.ConnectionError:
            print('Miner failed to load wallet')
        
        self.mining_thread.start()



    def shutdown_node(self):
        ''' Sends a request to the server to shutdown '''
        self.continue_mining = False
        url = 'http://localhost:{}/shutdown'.format(self.port)
        try:
            response = requests.post(url)
        except requests.exceptions.ConnectionError:
            pass
