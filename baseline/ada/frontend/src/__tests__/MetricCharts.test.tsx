import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi, afterEach } from 'vitest'
import MetricCharts from '../components/MetricCharts'

describe('MetricCharts missing-vs-zero semantics', () => {
  afterEach(() => vi.restoreAllMocks())

  it('renders missing metric points as gaps rather than zeroes', () => {
    // Step 2 and 4 are missing (null) — the chart must NOT plot them as 0.
    const series = [1.0, null, 1.2, 1.1, null, 0.9]
    const { container } = render(
      <MetricCharts metrics={{ loss: series, codebook_usage: [0.4, 0.5, 0.45] }} />,
    )
    const lossChart = container.querySelector('[data-testid="chart-Loss"] svg')!
    expect(lossChart).toHaveAttribute('data-missing-count', '2')

    const gaps = lossChart.querySelectorAll('[data-missing="true"]')
    expect(gaps.length).toBe(2)

    // Real zero would render as a circle at baseline; null renders a gap rect.
    const circles = lossChart.querySelectorAll('circle')
    expect(circles.length).toBe(series.length - 2)
  })

  it('renders a genuine zero as a real point, not a gap', () => {
    const { container } = render(<MetricCharts metrics={{ loss: [0, 0.1, 0.05] }} />)
    const chart = container.querySelector('[data-testid="chart-Loss"] svg')!
    expect(chart).toHaveAttribute('data-missing-count', '0')
    expect(chart.querySelectorAll('[data-missing="true"]').length).toBe(0)
    expect(chart.querySelectorAll('circle').length).toBe(3)
  })

  it('labels a series with no data as "no metric emitted"', () => {
    const { container } = render(<MetricCharts metrics={{ grad_norm: [] }} />)
    const chartDiv = container.querySelector('[data-testid="chart-Grad norm"]')!
    // Scope to the specific chart: all 6 series render this label when empty.
    expect(chartDiv.querySelector('.chart-meta')!.textContent).toBe('no metric emitted')
    const chart = chartDiv.querySelector('svg')!
    expect(chart).toHaveAttribute('data-missing-count', '0')
  })
})
