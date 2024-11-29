using Microsoft.AspNetCore.Mvc;
using PizzaOrder.Models;
using PizzaOrder.Services;

namespace PizzaOrder.Controllers;

[ApiController]
[Route("[controller]")]
public class OrderController : ControllerBase
{
    private readonly IOrderStateService _orderStateService;
    private readonly ILogger<OrderController> _logger;

    public OrderController(IOrderStateService orderStateService, ILogger<OrderController> logger)
    {
        _orderStateService = orderStateService;
        _logger = logger;
    }

    [HttpPost("/orders-sub")]
    public async Task<IActionResult> HandleOrderUpdate(CloudEvent<Order> cloudEvent)
    {
        _logger.LogInformation("Received order update for order {OrderId}", 
            cloudEvent.Data.OrderId);

        var result = await _orderStateService.UpdateOrderStateAsync(cloudEvent.Data);
        return Ok();
    }

    [HttpGet("{orderId}")]
    public async Task<ActionResult<Order>> GetOrder(string orderId)
    {
        var order = await _orderStateService.GetOrderAsync(orderId);
        
        if (order == null)
        {
            return NotFound();
        }

        return Ok(order);
    }
}