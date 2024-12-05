from flask import Flask, request, jsonify
from dapr.clients import DaprClient
import json
import time
import logging

APP_PORT = 8002
DAPR_PUBSUB_NAME = 'pizzapubsub'
DAPR_PUBSUB_TOPIC_NAME = 'orders'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def process_order(order_data):
    """Process the order and update its status"""
    try:
        # Simulate order processing steps
        stages = [
            ('validating', 1),
            ('processing', 2),
            ('confirmed', 1)
        ]
        
        with DaprClient() as client:
            for stage, duration in stages:
                order_data['status'] = stage
                logger.info(f"Order {order_data['order_id']} - {stage}")
                
                # Publish status update
                client.publish_event(
                    pubsub_name=DAPR_PUBSUB_NAME,
                    topic_name=DAPR_PUBSUB_TOPIC_NAME,
                    data=json.dumps(order_data)
                )
                
                time.sleep(duration)
        
        return order_data
        
    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        order_data['status'] = 'failed'
        order_data['error'] = str(e)
        return order_data

@app.route('/order', methods=['POST'])
def create_order():
    """Handle new order requests"""
    order_data = request.json
    logger.info(f"Received new order: {order_data['order_id']}")
    
    # Process the order
    result = process_order(order_data)
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=APP_PORT)