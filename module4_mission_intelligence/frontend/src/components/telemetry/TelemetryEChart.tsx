import React from 'react';
import ReactECharts from 'echarts-for-react';

interface TelemetryPoint {
  time: string;
  pressure: number | null;
  co2: number | null;
  radiation: number | null;
}

interface TelemetryEChartProps {
  data: TelemetryPoint[];
  height?: number;
}

export const TelemetryEChart: React.FC<TelemetryEChartProps> = ({ data, height = 260 }) => {
  const times = data.map((d) => d.time);
  const pressures = data.map((d) => d.pressure);
  const co2s = data.map((d) => d.co2);
  const radiations = data.map((d) => d.radiation);

  const option = {
    backgroundColor: '#060913',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#0F172A',
        },
      },
      backgroundColor: '#0F172A',
      borderColor: '#1E293B',
      borderWidth: 1,
      textStyle: {
        color: '#F8FAFC',
        fontSize: 11,
        fontFamily: 'monospace',
      },
    },
    legend: {
      data: ['Pressure (kPa)', 'Radiation (mSv/d)', 'CO2 (ppm)'],
      textStyle: {
        color: '#94A3B8',
        fontSize: 11,
        fontFamily: 'monospace',
      },
      top: 0,
    },
    grid: {
      left: '5%',
      right: '12%',
      bottom: '15%',
      top: '16%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: times,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'monospace' },
    },
    yAxis: [
      {
        type: 'value',
        name: 'Pressure (kPa)',
        position: 'left',
        min: 80,
        max: 115,
        axisLine: { show: true, lineStyle: { color: '#06B6D4' } },
        axisLabel: { color: '#06B6D4', fontSize: 10, fontFamily: 'monospace' },
        splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } },
      },
      {
        type: 'value',
        name: 'Radiation (mSv/d)',
        position: 'right',
        offset: 0,
        min: 0,
        max: 5,
        axisLine: { show: true, lineStyle: { color: '#EF4444' } },
        axisLabel: { color: '#EF4444', fontSize: 10, fontFamily: 'monospace' },
        splitLine: { show: false },
      },
      {
        type: 'value',
        name: 'CO2 (ppm)',
        position: 'right',
        offset: 45,
        min: 0,
        max: 4000,
        axisLine: { show: true, lineStyle: { color: '#F59E0B' } },
        axisLabel: { color: '#F59E0B', fontSize: 10, fontFamily: 'monospace' },
        splitLine: { show: false },
      },
    ],
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
      },
      {
        type: 'slider',
        show: true,
        bottom: 2,
        height: 14,
        borderColor: '#1E293B',
        backgroundColor: '#0F172A',
        fillerColor: 'rgba(239, 68, 68, 0.2)',
        handleStyle: {
          color: '#F59E0B',
          borderColor: '#F59E0B',
        },
        textStyle: {
          color: '#64748B',
          fontSize: 9,
        },
      },
    ],
    series: [
      {
        name: 'Pressure (kPa)',
        type: 'line',
        yAxisIndex: 0,
        data: pressures,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#06B6D4' },
      },
      {
        name: 'Radiation (mSv/d)',
        type: 'line',
        yAxisIndex: 1,
        data: radiations,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#EF4444' },
      },
      {
        name: 'CO2 (ppm)',
        type: 'line',
        yAxisIndex: 2,
        data: co2s,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#F59E0B' },
      },
    ],
  };

  return (
    <div className="w-full bg-[#060913] p-1 rounded-lg border border-[#1E293B]">
      <ReactECharts option={option} style={{ height: `${height}px`, width: '100%' }} notMerge={true} lazyUpdate={true} />
    </div>
  );
};

