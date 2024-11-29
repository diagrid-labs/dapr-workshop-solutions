using Dapr.Client;
using Dapr.Workflow;
using PizzaWorkflow.Models;

namespace PizzaWorkflow.Activities;

public class OrderActivity : WorkflowActivity<Order, Order>
{
    private readonly DaprClient _daprClient;
    private readonly ILogger<OrderActivity> _logger;

    public OrderActivity(DaprClient daprClient, ILogger<OrderActivity> logger)
    {
        _daprClient = daprClient;
        _logger = logger;
    }

    public override async Task<Order> RunAsync(WorkflowActivityContext context, Order order)
    {
        try
        {
            _logger.LogInformation("Starting ordering process for order {OrderId}", order.OrderId);
            
            var response = await _daprClient.InvokeMethodAsync<Order, Order>(
                HttpMethod.Post,
                "pizza-store",
                "order",
                order);

            _logger.LogInformation("Order {OrderId} processed with status {Status}", 
                order.OrderId, response.Status);
            
            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing order {OrderId}", order.OrderId);
            throw;
        }
    }
}
