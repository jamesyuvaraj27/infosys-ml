Chart.defaults.color = '#9CA3AF';
Chart.defaults.font.family = 'Inter';

document.addEventListener('DOMContentLoaded', () => {
  const marketData = window.marketData;
  const competitors = window.competitors;

  const trendCanvas = document.getElementById('marketTrendChart');
  if (trendCanvas && marketData && marketData.market_trend) {
    const ctx = trendCanvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.4)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');

    new Chart(trendCanvas, {
      type: 'line',
      data: {
        labels: marketData.market_trend.map((p) => p.year),
        datasets: [
          {
            label: 'Market Size',
            data: marketData.market_trend.map((p) => p.value),
            borderColor: '#3B82F6',
            backgroundColor: gradient,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#3B82F6',
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#9CA3AF' } },
          y: { grid: { display: false }, ticks: { color: '#9CA3AF' } },
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
            backgroundColor: ['#3B82F6', '#A855F7', '#EC4899'],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#9CA3AF' } },
        },
      },
    });
  }
});
