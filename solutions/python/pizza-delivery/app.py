# pizza-delivery/app.py
from flask import Flask, request, jsonify
from dapr.clients import DaprClient
import json
import time
import logging

APP_PORT = 8004
DAPR_PUBSUB_NAME = 'pizzapubsub'
DAPR_PUBSUB_TOPIC_NAME = 'orders'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def deliver_pizza(order_data):
    """Handle the delivery process and update status"""
    try:
        # Simulate delivery stages
        stages = [
            ('finding_driver', 2),
            ('driver_assigned', 1),
            ('picked_up', 2),
            ('on_the_way', 5),
            ('arriving', 2),
            ('at_location', 1)
        ]
        
        with DaprClient() as client:
            for stage, duration in stages:
                order_data['status'] = f'delivery_{stage}'
                logger.info(f"Order {order_data['order_id']} - {stage}")
                
                # Publish status update
                client.publish_event(
                    pubsub_name=DAPR_PUBSUB_NAME,
                    topic_name=DAPR_PUBSUB_TOPIC_NAME,
                    data=json.dumps(order_data)
                )
                
                time.sleep(duration)
        
        order_data['status'] = 'delivered'
        logger.info(f"Order {order_data['order_id']} - delivery completed")
        
        return order_data
        
    except Exception as e:
        logger.error(f"Error delivering pizza: {str(e)}")
        order_data['status'] = 'delivery_failed'
        order_data['error'] = str(e)
        return order_data

@app.route('/deliver', methods=['POST'])
def start_delivery():
    """Handle delivery requests"""
    order_data = request.json
    logger.info(f"Starting delivery for order: {order_data['order_id']}")
    
    # Deliver the pizza
    result = deliver_pizza(order_data)
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=APP_PORT)