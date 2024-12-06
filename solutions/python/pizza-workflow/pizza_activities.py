from dapr.ext.workflow import WorkflowActivityContext
from dapr.clients import DaprClient
import json
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

def order_pizza(ctx: WorkflowActivityContext, input_: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to place pizza order via pizza-storefront service"""
    logger.info(f"Calling pizza-storefront service for order {input_['order_id']}")

    # Call the pizza-storefront service to order the pizza
    app_id = 'pizza-storefront'
    headers = {'dapr-app-id': app_id, 'content-type': 'application/json'}

    base_url = 'http://localhost'
    dapr_http_port = 3505
    method = 'order'
    target_url = '%s:%s/%s' % (base_url, dapr_http_port, method)

    response = requests.post(
        url=target_url,
        data=json.dumps(input_),
        headers=headers
    )

    return json.loads(response.content)

def cook_pizza(ctx: WorkflowActivityContext, input_: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to cook pizza via pizza-kitchen service"""
    logger.info(f"Calling pizza-kitchen service for order {input_['order_id']}")
    
    # Call the pizza-kitchen service to  the pizza
    app_id = 'pizza-kitchen'
    headers = {'dapr-app-id': app_id, 'content-type': 'application/json'}

    base_url = 'http://localhost'
    dapr_http_port = 3505
    method = 'cook'
    target_url = '%s:%s/%s' % (base_url, dapr_http_port, method)

    response = requests.post(
        url=target_url,
        data=json.dumps(input_),
        headers=headers
    )

    return json.loads(response.content)

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
    
    # Call the pizza-delivery service to  the pizza
    app_id = 'pizza-delivery'
    headers = {'dapr-app-id': app_id, 'content-type': 'application/json'}

    base_url = 'http://localhost'
    dapr_http_port = 3505
    method = 'deliver'
    target_url = '%s:%s/%s' % (base_url, dapr_http_port, method)

    response = requests.post(
        url=target_url,
        data=json.dumps(input_),
        headers=headers
    )
    print('result: ' + response.text, flush=True)
    return json.loads(response.content)