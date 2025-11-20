// charts.js

// Sales Chart
function createSalesChart(ctx, data) {
    const salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Sales',
                data: data.values,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                },
            },
        },
    });
    return salesChart;
}

// Inventory Chart
function createInventoryChart(ctx, data) {
    const inventoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Inventory',
                data: data.values,
                backgroundColor: 'rgba(153, 102, 255, 0.5)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                },
            },
        },
    });
    return inventoryChart;
}

// Orders Chart
function createOrdersChart(ctx, data) {
    const ordersChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Orders',
                data: data.values,
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
                hoverOffset: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                },
            },
        },
    });
    return ordersChart;
}

// Revenue Chart
function createRevenueChart(ctx, data) {
    const revenueChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Revenue',
                data: data.values,
                backgroundColor: ['#42A5F5', '#66BB6A', '#FFA726'],
                hoverOffset: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                },
            },
        },
    });
    return revenueChart;
}