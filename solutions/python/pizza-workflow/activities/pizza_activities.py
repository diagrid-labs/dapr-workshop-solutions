from dapr.ext.workflow import WorkflowActivityContext
from dapr.clients import DaprClient
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def order_pizza(ctx: WorkflowActivityContext, input_: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to place pizza order via pizza-store service"""
    logger.info(f"Calling pizza-store service for order {input_['order_id']}")
    with DaprClient() as client:
        response = client.invoke_method(
            'pizza-store',
            'order',
            data=json.dumps(input_),
            http_verb='POST'
        )
        return json.loads(response.data)

def cook_pizza(ctx: WorkflowActivityContext, input_: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to cook pizza via pizza-kitchen service"""
    logger.info(f"Calling pizza-kitchen service for order {input_['order_id']}")
    with DaprClient() as client:
        response = client.invoke_method(
            'pizza-kitchen',
            'cook',
            data=json.dumps(input_),
            http_verb='POST'
        )
        return json.loads(response.data)

def validate_pizza(ctx: WorkflowActivityContext, input_: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to handle pizza validation"""
    logger.info(f"Starting validation process for order {input_['order_id']}")
    # Store validation request in state store
    with DaprClient() as client:
        client.save_state(
            store_name="pizzastatestore",
            key=f"validation_{input_['order_id']}",
            value=json.dumps({
                "order_id": input_['order_id'],
                "status": "pending_validation"
            })
        )
    return input_

def deliver_pizza(ctx: WorkflowActivityContext, input_: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to deliver pizza via pizza-delivery service"""
    logger.info(f"Calling pizza-delivery service for order {input_['order_id']}")
    with DaprClient() as client:
        response = client.invoke_method(
            'pizza-delivery',
            'deliver',
            data=json.dumps(input_),
            http_verb='POST'
        )
        return json.loads(response.data)