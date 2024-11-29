using Microsoft.AspNetCore.Mvc;
using PizzaStore.Models;
using PizzaStore.Services;

namespace PizzaStore.Controllers;

[ApiController]
[Route("[controller]")]
public class OrderController : ControllerBase
{
    private readonly IOrderProcessingService _orderService;
    private readonly ILogger<OrderController> _logger;

    public OrderController(IOrderProcessingService orderService, ILogger<OrderController> logger)
    {
        _orderService = orderService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<ActionResult<Order>> CreateOrder(Order order)
    {
        _logger.LogInformation("Received new order: {OrderId}", order.OrderId);
        var result = await _orderService.ProcessOrderAsync(order);
        return Ok(result);
    }
}