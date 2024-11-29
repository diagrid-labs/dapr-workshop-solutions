from dapr.ext.workflow import DaprWorkflowContext
from typing import Dict, Any
import logging

from pizza_activities import order_pizza, cook_pizza, deliver_pizza

logger = logging.getLogger(__name__)

def pizza_workflow(context: DaprWorkflowContext, order_data: Dict[str, Any]):
    """Orchestrate the pizza order process"""
    try:
        logger.info(f"Starting workflow for order {order_data['order_id']}")
        
        # Step 1: Place and process the order
        logger.info(f"Placing order {order_data['order_id']}")
        order_result = yield context.call_activity(  
            order_pizza,  
            input=order_data
        )
        
        if order_result.get('status') != 'confirmed':
            raise Exception(f"Order failed: {order_result.get('error', 'Unknown error')}")
        
        # Step 2: Cook the pizza
        logger.info(f"Starting cooking for order {order_data['order_id']}")
        cooking_result = yield context.call_activity(  
            cook_pizza,  
            input=order_result
        )
        
        if cooking_result.get('status') != 'cooked':
            raise Exception(f"Cooking failed: {cooking_result.get('error', 'Unknown error')}")
        
        # Step 3: Wait for manager validation
        logger.info(f"Waiting for manager validation of order {order_data['order_id']}")
        validation_event = yield context.wait_for_external_event("ValidationComplete")  
        
        if not validation_event.get('approved'):
            raise Exception("Pizza validation failed - need to remake")
        
        # Step 4: Deliver the pizza
        logger.info(f"Starting delivery for order {order_data['order_id']}")
        delivery_result = yield context.call_activity(  
            deliver_pizza,  
            input=cooking_result
        )
        
        if delivery_result.get('status') != 'delivered':
            raise Exception(f"Delivery failed: {delivery_result.get('error', 'Unknown error')}")
        
        return {
            "order_id": order_data["order_id"],
            "status": "completed",
            "final_status": "delivered",
            "delivery_result": delivery_result
        }
        
    except Exception as e:
        logger.error(f"Workflow failed for order {order_data['order_id']}: {str(e)}")
        return {
            "order_id": order_data["order_id"],
            "status": "failed",
            "error": str(e)
        }