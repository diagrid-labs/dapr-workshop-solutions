using Dapr.Client;
using PizzaOrder.Models;
using System.Text.Json;

namespace PizzaOrder.Services;

public interface IOrderStateService
{
    Task<Order> UpdateOrderStateAsync(Order order);
    Task<Order?> GetOrderAsync(string orderId);
}

public class OrderStateService : IOrderStateService
{
    private readonly DaprClient _daprClient;
    private readonly ILogger<OrderStateService> _logger;
    private const string STORE_NAME = "pizzastatestore";

    public OrderStateService(DaprClient daprClient, ILogger<OrderStateService> logger)
    {
        _daprClient = daprClient;
        _logger = logger;
    }

    public async Task<Order> UpdateOrderStateAsync(Order order)
    {
        try
        {
            var stateKey = $"order_{order.OrderId}";
            
            // Try to get existing state
            var existingState = await _daprClient.GetStateAsync<Order>(STORE_NAME, stateKey);
            if (existingState != null)
            {
                // Merge new data with existing state
                order = MergeOrderStates(existingState, order);
            }

            // Save updated state
            await _daprClient.SaveStateAsync(STORE_NAME, stateKey, order);
            _logger.LogInformation("Updated state for order {OrderId} - Status: {Status}", 
                order.OrderId, order.Status);

            return order;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating state for order {OrderId}", order.OrderId);
            throw;
        }
    }

    public async Task<Order?> GetOrderAsync(string orderId)
    {
        try
        {
            var stateKey = $"order_{orderId}";
            var order = await _daprClient.GetStateAsync<Order>(STORE_NAME, stateKey);
            
            if (order == null)
            {
                _logger.LogWarning("Order {OrderId} not found", orderId);
                return null;
            }

            return order;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving order {OrderId}", orderId);
            throw;
        }
    }

    private Order MergeOrderStates(Order existing, Order update)
    {
        // Preserve important fields from existing state
        update.Customer = update.Customer ?? existing.Customer;
        update.PizzaType = update.PizzaType ?? existing.PizzaType;
        update.Size = update.Size ?? existing.Size;
        
        return update;
    }
}