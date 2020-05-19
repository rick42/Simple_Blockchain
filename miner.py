import os
import requests
import threading

class Miner:
    def __init__(self, port, hash_rate=None, miner_list=None, blocks_to_update=5, time_per_block=10):
        self.port = port
        self.hash_rate = hash_rate
        self.node_thread = threading.Thread(target=self.start_server)
        self.mining_thread = threading.Thread(target=self.mine)
        self.continue_mining = False
        self.blocks_to_update = blocks_to_update
        self.time_per_block = time_per_block
        self.setup_node()
        if miner_list != None:
            self.establish_network(miner_list)
            self.start_mining()
        print('MINER CREATED: port={}  hashrate={}  blocks_to_update={}  time_per_block={}'.format(port, hash_rate, blocks_to_update, time_per_block))


    def resolve_node_conflicts(self):
        ''' Make a request to update the miner's blockchain to the longest
        blockchain amongst all nodes in the network '''
        url = 'http://localhost:{}/resolve-conflicts'.format(self.port)
        try:
            response = requests.post(url)
        except requests.exceptions.ConnectionError:
            print('Miner unable to resolve conflicts',self.port)


    def mine(self):
        ''' Target function of self.mining_thread, it automamically mines blocks
        until it is signalled to stop '''
        self.continue_mining = True
        url = 'http://localhost:{}/mine'.format(self.port)
        self.resolve_node_conflicts()
        while self.continue_mining == True:
            try:
                response = requests.post(url)
            except requests.exceptions.ConnectionError:
                print('MINING FAILED: Unable to connect to server ',self.port)
                self.continue_mining = False
            if response.status_code != 201:
                self.resolve_node_conflicts()
        

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
        os.system("python node.py --port {} --hashrate {} --avgtime {} --difficulty_update".format(self.port,self.hash_rate,self.time_per_block,self.blocks_to_update))

    
    def establish_network(self,miner_list):
        ''' Create a two way connection with each miner in miner_list '''
        for miner in miner_list:
            self.add_peer_node(miner.port)
            miner.add_peer_node(self.port)


    def add_peer_node(self, peer_port):
        ''' Add peer_port to the miner's list of peers '''
        if peer_port == self.port:
            return
        url = 'http://localhost:{}/node'.format(self.port)
        try:
            response = requests.post(url, json={'node': 'localhost:{}'.format(peer_port)})
        except requests.exceptions.ConnectionError:
            print('Failed to add peer node')

    
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

        
        
        #self.mining_thread.start()


    def shutdown_node(self):
        ''' Sends a request to the server to shutdown '''
        self.continue_mining = False
        url = 'http://localhost:{}/shutdown'.format(self.port)
        try:
            response = requests.post(url)
        except requests.exceptions.ConnectionError:
            pass
