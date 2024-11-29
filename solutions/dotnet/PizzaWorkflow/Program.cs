// Program.cs
using Dapr.Workflow;
using PizzaWorkflow.Activities;
using PizzaWorkflow.Workflows;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers().AddDapr();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add Dapr Workflow
builder.Services.AddDaprWorkflow(options =>
{
    // Register workflows
    options.RegisterWorkflow<PizzaOrderingWorkflow>();

    // Register activities
    options.RegisterActivity<OrderActivity>();
    options.RegisterActivity<CookingActivity>();
    options.RegisterActivity<ValidationActivity>();
    options.RegisterActivity<DeliveryActivity>();
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapControllers();
app.Run();