from flask import Flask, request, jsonify
from dapr.clients import DaprClient
import json
import logging

APP_PORT = 8001
DAPR_STORE_NAME = 'pizzastatestore'
DAPR_PUBSUB_NAME = 'pizzapubsub'
DAPR_PUBSUB_TOPIC_NAME = 'orders'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/orders-sub', methods=['POST'])
def orders_subscription():
    """Handle order updates from pub/sub"""
    event = request.json
    
    try:
        # Get the order data from the event
        order_data = json.loads(event['data'])
        order_id = order_data['order_id']
        
        logger.info(f"Received order update for order {order_id}: {order_data['status']}")
        
        # Save order state
        with DaprClient() as client:
            # Get existing order data if any
            state_key = f"order_{order_id}"
            try:
                state = client.get_state(
                    store_name=DAPR_STORE_NAME,
                    key=state_key
                )
                existing_order = json.loads(state.data) if state.data else {}
            except Exception:
                existing_order = {}
            
            # Update with new data
            updated_order = {**existing_order, **order_data}
            
            # Save updated state
            client.save_state(
                store_name=DAPR_STORE_NAME,
                key=state_key,
                value=json.dumps(updated_order)
            )
            
            logger.info(f"Updated state for order {order_id}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error processing order update: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/order', methods=['POST'])
def create_order():
    """Create a new order"""
    order_data = request.json
    order_id = order_data['order_id']
    
    try:
        # Save order state
        with DaprClient() as client:
            client.save_state(
                store_name=DAPR_STORE_NAME,
                key=f"order_{order_id}",
                value=json.dumps(order_data)
            )
            
            logger.info(f"Created order {order_id}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error creating order {order_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/order/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details from state store"""
    try:
        with DaprClient() as client:
            state = client.get_state(
                store_name=DAPR_STORE_NAME,
                key=f"order_{order_id}"
            )
            
            if not state.data:
                return jsonify({'error': 'Order not found'}), 404
                
            order_data = json.loads(state.data)
            return jsonify(order_data)
            
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete order details from state store"""
    try:
        with DaprClient() as client:
            client.delete_state(
                store_name=DAPR_STORE_NAME,
                key=f"order_{order_id}"
            )
            
            return jsonify({'success': True})
            
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(port=APP_PORT)