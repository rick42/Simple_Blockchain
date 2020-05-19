from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from flask import Response, render_template
import json
from datetime import datetime
import time

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)



@app.route('/shutdown', methods=['POST'])
def shutdown():
    """ shutdown() turns off the flask server when called """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('ui', 'node.html')

@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')

@app.route('/statistics', methods=['GET'])
def get_statistic_ui():
    return send_from_directory('ui', 'statistics.html')

# @app.route('/chart-data-hr')
# def chart_data():
#     def generate_data():
#         while True: 
#             json_data = json.dumps({
#                 'time':  datetime.now().strftime('%H:%M:%S'),
#                 'value': blockchain.chain[-1].index
#             })

#             yield f"data:{json_data}\n\n"
#             time.sleep(1)

#     return Response(generate_data(), mimetype='text/event-stream')

# @app.route('/chart-data-hr')
# def chart_data():
#     def generate_data():
#         while True: 
#             json_data = json.dumps({
#                 'time':  datetime.now().strftime('%H:%M:%S'),
#                 'value': blockchain.chain[-1].bits
#             })

#             yield f"data:{json_data}\n\n"
#             time.sleep(1)

# return Response(generate_data(), mimetype='text/event-stream')

@app.route('/Average-Time')
def chart_data():
    def generate_data():
        blocks_to_update = blockchain.blocks_to_update

        while True: 
            if blockchain.chain[-1].index  == (blocks_to_update - 1):
                first_block_secs = blockchain.chain[-1 * blocks_to_update ].timestamp
                last_block_secs = blockchain.chain[-1].timestamp 
                time_span_secs = last_block_secs - first_block_secs 
                avg_time_block= time_span_secs / (blocks_to_update - 1)
                json_data = json.dumps({
                    'time':  datetime.now().strftime('%H:%M:%S'),
                    'value': avg_time_block
                })
                yield f"data:{json_data}\n\n"
            
            # elif ((blockchain.chain[-1].index + 1) %  blocks_to_update) == 0:
            elif ((blockchain.chain[-1].index + 1) >=  blocks_to_update):
                first_block_secs = blockchain.chain[-1 * (blocks_to_update + 1)].timestamp
                last_block_secs = blockchain.chain[-1].timestamp 
                time_span_secs = last_block_secs - first_block_secs
                avg_time_block= time_span_secs / blocks_to_update

                json_data = json.dumps({
                    'time':  datetime.now().strftime('%H:%M:%S'),
                    'value': avg_time_block
                })
                yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_data(), mimetype='text/event-stream')

@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port, blocks_to_update, time_per_block, hash_rate)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port, blocks_to_update, time_per_block, hash_rate)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading the keys failed.'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'messsage': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(
        values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):     
            blockchain.halt_mining = True
            response = {'message': 'Block added'}
            return jsonify(response), 201
        else:
            blockchain.resolve_conflicts = True
            response = {'message': 'Block seems invalid.'}
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index:
        response = {'message': 'Blockchain seems to differ from local blockchain.'}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else: 
        response = {'message': 'Blockchain seems to be shorter, block not added'}
        return jsonify(response), 408


@app.route('/halt_mining', methods=['POST'])
def halt_mining():
    blockchain.halt_mining = True
    response = {
        'message': 'blockchain.halt_mining set to True'
    }
    return jsonify(response), 200


@app.route('/test_resolve', methods=['POST'])
def test_resolve():
    ''' This route is for testing purposes '''
    blockchain.resolve_conflicts = True
    response = {
        'message': 'blockchain.resolve_conflict set to True'
    }
    return jsonify(response), 200


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.resolve_conflicts:
        response = {'message': 'Resolve conflicts first, block not added!'}
        return jsonify(response), 409
    if blockchain.is_mining:
        response = {'message': 'Mining already in progress, block not added!'}
        return jsonify(response), 400
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully.',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {'message': 'Chain was replaced!'}
    else:
        response = {'message': 'Local chain kept!'}
    return jsonify(response), 200


@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No node data found.'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message': 'No node found.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('-r', '--hashrate', type=int)
    
    parser.add_argument('-t', '--avgtime', type=int, default=10)
    parser.add_argument('-b', '--difficulty_update', type=int, default=5)
    
    args = parser.parse_args()
    port = args.port
    hash_rate = args.hashrate
    wallet = Wallet(port)
    time_per_block = args.avgtime
    blocks_to_update = args.difficulty_update

    blockchain = Blockchain(wallet.public_key, port, blocks_to_update, time_per_block)
   # blockchain.hash_rate = hash_rate
    # blockchain.blocks_to_update= blocks_to_update
    # blockchain.time_per_block  = time_per_block
 
    app.run(host='0.0.0.0', port=port)
