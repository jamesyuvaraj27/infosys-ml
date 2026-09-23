Chart.defaults.color = '#64748B';
Chart.defaults.font.family = 'Inter';

document.addEventListener('DOMContentLoaded', () => {
  const marketData = window.marketData;
  const competitors = window.competitors;

  const trendCanvas = document.getElementById('marketTrendChart');
  if (trendCanvas && marketData && marketData.market_trend) {
    const ctx = trendCanvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 180);
    gradient.addColorStop(0, 'rgba(37, 99, 235, 0.25)');
    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.02)');

    new Chart(trendCanvas, {
      type: 'line',
      data: {
        labels: marketData.market_trend.map((p) => p.year),
        datasets: [
          {
            label: 'Market Size',
            data: marketData.market_trend.map((p) => p.value),
            borderColor: '#2563EB',
            borderWidth: 2,
            backgroundColor: gradient,
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#2563EB',
            pointRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#F1F5F9' }, ticks: { color: '#64748B', font: { size: 11 } } },
          y: { grid: { color: '#F1F5F9' }, ticks: { color: '#64748B', font: { size: 11 } } },
        },
      },
    });
  }

  const compCanvas = document.getElementById('competitorChart');
  if (compCanvas && competitors) {
    new Chart(compCanvas, {
      type: 'doughnut',
      data: {
        labels: competitors.map((c) => c.name),
        datasets: [
          {
            data: competitors.map((c) => c.market_share),
            backgroundColor: ['#2563EB', '#7C3AED', '#EC4899', '#10B981'],
            borderWidth: 2,
            borderColor: '#FFFFFF',
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#475569', boxWidth: 12, font: { size: 11 } } },
        },
      },
    });
  }
});
