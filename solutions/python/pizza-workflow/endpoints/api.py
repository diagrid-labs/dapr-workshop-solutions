from flask import Blueprint, request, jsonify
from dapr.clients import DaprClient

api = Blueprint('api', __name__)

@api.route('/start-order', methods=['POST'])
def start_order():
    order_data = request.json
    instance_id = f"pizza-order-{order_data['order_id']}"
    
    with DaprClient() as client:
        # Start workflow using the Dapr Client
        result = client.start_workflow(
            workflow_component="dapr",
            workflow_name="pizza_workflow",
            instance_id=instance_id,
            input=order_data
        )
    
    return jsonify({
        "order_id": order_data["order_id"],
        "workflow_instance_id": instance_id,
        "status": "started"
    })

@api.route('/validate-pizza', methods=['POST'])
def validate_pizza():
    validation_data = request.json
    order_id = validation_data["order_id"]
    approved = validation_data["approved"]
    
    with DaprClient() as client:
        # Raise workflow event using the Dapr Client
        client.raise_workflow_event(
            workflow_component="dapr",
            instance_id=f"pizza-order-{order_id}",
            event_name="ValidationComplete",
            event_data={"approved": approved}
        )
    
    return jsonify({
        "order_id": order_id,
        "validation_status": "approved" if approved else "rejected"
    })