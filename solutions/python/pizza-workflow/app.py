from flask import Flask, request, jsonify
from dapr.clients import DaprClient
from dapr.ext.workflow import WorkflowRuntime
import logging
import threading
from activities.pizza_activities import order_pizza, cook_pizza, validate_pizza, deliver_pizza
from workflows.pizza_workflow import pizza_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# API endpoints
@app.route('/start-order', methods=['POST'])
def start_order():
    order_data = request.json
    instance_id = f"pizza-order-{order_data['order_id']}"
    
    with DaprClient() as client:
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

@app.route('/validate-pizza', methods=['POST'])
def validate_pizza_endpoint():
    validation_data = request.json
    order_id = validation_data["order_id"]
    
    with DaprClient() as client:
        client.raise_workflow_event(
            workflow_component="dapr",
            instance_id=f"pizza-order-{order_id}",
            event_name="ValidationComplete",
            event_data=validation_data
        )
    
    return jsonify({
        "order_id": order_id,
        "validation_status": "approved" if validation_data.get("approved") else "rejected"
    })

def run_workflow_runtime():
    logger.info("Initializing workflow runtime")
    workflow_runtime = WorkflowRuntime()
    
    # Register workflow and activities
    workflow_runtime.register_workflow(pizza_workflow)
    workflow_runtime.register_activity(order_pizza)
    workflow_runtime.register_activity(cook_pizza)
    workflow_runtime.register_activity(validate_pizza)
    workflow_runtime.register_activity(deliver_pizza)
    
    logger.info("Starting workflow runtime")
    workflow_runtime.start()

if __name__ == "__main__":
    # Start workflow runtime in a separate thread
    workflow_thread = threading.Thread(target=run_workflow_runtime, daemon=True)
    workflow_thread.start()
    
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=8004)