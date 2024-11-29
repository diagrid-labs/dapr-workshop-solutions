using Dapr.Client;
using Microsoft.AspNetCore.Mvc;
using PizzaWorkflow.Models;
using PizzaWorkflow.Workflows;

namespace PizzaWorkflow.Controllers;

[ApiController]
[Route("[controller]")]
public class WorkflowController : ControllerBase
{
    private readonly DaprClient _daprClient;
    private readonly ILogger<WorkflowController> _logger;

    public WorkflowController(DaprClient daprClient, ILogger<WorkflowController> logger)
    {
        _daprClient = daprClient;
        _logger = logger;
    }

    [HttpPost("start-order")]
    public async Task<IActionResult> StartOrder(Order order)
    {
        var instanceId = $"pizza-order-{order.OrderId}";
        
        try
        {
            _logger.LogInformation("Starting workflow for order {OrderId}", order.OrderId);

            await _daprClient.StartWorkflowAsync(
                workflowComponent: "dapr",
                workflowName: nameof(PizzaOrderingWorkflow),
                input: order,
                instanceId: instanceId);

            _logger.LogInformation("Workflow started successfully for order {OrderId}", order.OrderId);

            return Ok(new
            {
                order_id = order.OrderId,
                workflow_instance_id = instanceId,
                status = "started"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to start workflow for order {OrderId}", order.OrderId);
            throw;
        }
    }

    [HttpPost("validate-pizza")]
    public async Task<IActionResult> ValidatePizza(ValidationRequest validation)
    {
        var instanceId = $"pizza-order-{validation.OrderId}";
        
        try
        {
            _logger.LogInformation("Raising validation event for order {OrderId}. Approved: {Approved}", 
                validation.OrderId, validation.Approved);

            await _daprClient.RaiseWorkflowEventAsync(
                instanceId: instanceId,
                workflowComponent: "dapr",
                eventName: "ValidationComplete",
                eventData: validation);

            _logger.LogInformation("Validation event raised successfully for order {OrderId}", 
                validation.OrderId);

            return Ok(new
            {
                order_id = validation.OrderId,
                validation_status = validation.Approved ? "approved" : "rejected"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to raise validation event for order {OrderId}", validation.OrderId);
            throw;
        }
    }
}