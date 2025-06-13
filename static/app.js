// TrainingPeaks-style Chart.js integration for Do The Work App

function initChart(data) {
    const ctx = document.getElementById('caloriesChart');
    if (!ctx) {
        console.error('Chart canvas not found');
        return;
    }

    // TrainingPeaks-inspired color scheme
    const primaryColor = '#0077be';
    const primaryGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    primaryGradient.addColorStop(0, 'rgba(0, 119, 190, 0.8)');
    primaryGradient.addColorStop(1, 'rgba(0, 119, 190, 0.2)');

    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Daily Active Calories',
                data: data.values,
                backgroundColor: primaryGradient,
                borderColor: primaryColor,
                borderWidth: 2,
                borderRadius: 6,
                borderSkipped: false,
                hoverBackgroundColor: 'rgba(0, 119, 190, 0.9)',
                hoverBorderColor: primaryColor,
                hoverBorderWidth: 3
            }, {
                type: 'line',
                label: 'Annual Average',
                data: Array(data.labels.length).fill(data.annualAverage),
                borderColor: '#ff6b35',
                backgroundColor: 'rgba(255, 107, 53, 0.1)',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0,
                pointHoverRadius: 0,
                fill: false,
                tension: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'center',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            family: 'Inter'
                        },
                        color: '#64748b',
                        filter: function(legendItem, chartData) {
                            // Only show the Annual Average legend
                            return legendItem.text === 'Annual Average';
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#0077be',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false,
                    titleFont: {
                        size: 14,
                        weight: '600'
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 12,
                    callbacks: {
                        title: function(tooltipItems) {
                            return tooltipItems[0].label;
                        },
                        label: function(context) {
                            if (context.dataset.label === 'Annual Average') {
                                return 'Annual Average: ' + Math.round(context.parsed.y) + ' calories/day';
                            }
                            return Math.round(context.parsed.y) + ' calories/day';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(226, 232, 240, 0.6)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: {
                            size: 12,
                            family: 'Inter'
                        },
                        padding: 8,
                        callback: function(value, index, values) {
                            return Math.round(value);
                        }
                    },
                    title: {
                        display: true,
                        text: 'Active Calories per Day',
                        color: '#475569',
                        font: {
                            size: 13,
                            weight: '500',
                            family: 'Inter'
                        },
                        padding: {
                            top: 20
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: {
                            size: 12,
                            family: 'Inter'
                        },
                        maxRotation: 45,
                        minRotation: 0
                    }
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            elements: {
                bar: {
                    borderWidth: 2
                }
            }
        }
    });

    // Add chart hover effects
    ctx.addEventListener('mousemove', function(event) {
        const points = chart.getElementsAtEventForMode(event, 'nearest', { intersect: false }, true);
        
        if (points.length) {
            ctx.style.cursor = 'pointer';
        } else {
            ctx.style.cursor = 'default';
        }
    });
    
    return chart;
}

// Utility function to format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Animate stat cards on load
document.addEventListener('DOMContentLoaded', function() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });

    // Animate chart section
    const chartSection = document.querySelector('.chart-section');
    if (chartSection) {
        chartSection.style.opacity = '0';
        chartSection.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            chartSection.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            chartSection.style.opacity = '1';
            chartSection.style.transform = 'translateY(0)';
        }, 300);
    }

    // Animate insights cards
    const insightCards = document.querySelectorAll('.insight-card');
    insightCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 600 + (index * 100));
    });
});

// Form validation and enhancement
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        const submitButton = loginForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        loginForm.addEventListener('submit', function() {
            submitButton.disabled = true;
            submitButton.textContent = 'Connecting...';
            submitButton.style.opacity = '0.7';
            
            // Re-enable after 5 seconds as fallback
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
                submitButton.style.opacity = '1';
            }, 5000);
        });
    }
});

// Add loading state for dashboard
window.addEventListener('beforeunload', function() {
    const body = document.body;
    body.style.opacity = '0.7';
    body.style.pointerEvents = 'none';
}); 