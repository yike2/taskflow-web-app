<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  pending: {
    type: Number,
    default: 0
  },
  inProgress: {
    type: Number,
    default: 0
  },
  completed: {
    type: Number,
    default: 0
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')

  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Pending', 'In Progress', 'Completed'],
      datasets: [{
        data: [props.pending, props.inProgress, props.completed],
        backgroundColor: [
          '#fbbf24',
          '#3b82f6',
          '#10b981'
        ],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
        },
        title: {
          display: true,
          text: 'Task Status Distribution',
          font: {
            size: 16,
            weight: '600'
          }
        }
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch([() => props.pending, () => props.inProgress, () => props.completed], () => {
  createChart()
})
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>