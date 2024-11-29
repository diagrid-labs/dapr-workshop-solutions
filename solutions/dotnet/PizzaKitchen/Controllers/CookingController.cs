using Microsoft.AspNetCore.Mvc;
using PizzaKitchen.Models;
using PizzaKitchen.Services;

namespace PizzaKitchen.Controllers;

[ApiController]
[Route("[controller]")]
public class CookingController : ControllerBase
{
    private readonly ICookingService _cookingService;
    private readonly ILogger<CookingController> _logger;

    public CookingController(ICookingService cookingService, ILogger<CookingController> logger)
    {
        _cookingService = cookingService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<ActionResult<Order>> Cook(Order order)
    {
        _logger.LogInformation("Starting cooking for order: {OrderId}", order.OrderId);
        var result = await _cookingService.CookPizzaAsync(order);
        return Ok(result);
    }
}