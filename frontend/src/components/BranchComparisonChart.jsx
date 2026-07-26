import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Building2, GraduationCap, Medal, TrendingUp } from 'lucide-react';

function BranchTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  if (!item) return null;

  return (
    <div className="branch-chart-tooltip">
      <div className="branch-chart-tooltip__title">
        <Building2 size={15} />
        <strong>{item.name}</strong>
      </div>
      <div className="branch-chart-tooltip__row">
        <span>O‘quvchilar</span>
        <b>{item.students}</b>
      </div>
      <div className="branch-chart-tooltip__row">
        <span>O‘rtacha natija</span>
        <b>{item.average}%</b>
      </div>
    </div>
  );
}

function BranchNameTick({ x, y, payload, rows }) {
  const row = rows.find((item) => item.name === payload.value);
  const label = payload.value.length > 16 ? `${payload.value.slice(0, 16)}…` : payload.value;

  return (
    <g transform={`translate(${x},${y})`}>
      <text x={-10} y={-4} textAnchor="end" className="branch-chart-axis-name">{label}</text>
      <text x={-10} y={11} textAnchor="end" className="branch-chart-axis-meta">{row?.students || 0} o‘quvchi</text>
    </g>
  );
}

function AverageLabel({ x, y, width, height, value }) {
  const inside = width > 52;
  return (
    <text
      x={inside ? x + width - 10 : x + width + 8}
      y={y + height / 2 + 4}
      textAnchor={inside ? 'end' : 'start'}
      className={inside ? 'branch-chart-bar-label is-inside' : 'branch-chart-bar-label'}
    >
      {Number(value || 0).toFixed(0)}%
    </text>
  );
}

export default function BranchComparisonChart({ data = [], title = "Filiallar bo‘yicha taqqoslash", description = "Har bir filialning o‘rtacha natijasi va o‘quvchilar soni." }) {
  const rows = data
    .map((item) => ({
      name: item.name || item.filial || item.filial_nomi || 'Noma’lum',
      students: Number(item.students ?? item.oquvchilar ?? item.oquvchilar_soni ?? 0),
      average: Math.max(0, Math.min(100, Number(item.average ?? item.ortacha ?? item.ortacha_foiz ?? 0))),
    }))
    .sort((a, b) => b.average - a.average || b.students - a.students);

  if (!rows.length) return null;

  const bestResult = rows[0];
  const mostStudents = [...rows].sort((a, b) => b.students - a.students)[0];
  const totalStudents = rows.reduce((sum, item) => sum + item.students, 0);
  const chartHeight = Math.max(270, Math.min(660, rows.length * 54 + 70));

  return (
    <div className="branch-comparison">
      <div className="branch-comparison__header">
        <div>
          <div className="branch-comparison__eyebrow"><TrendingUp size={14} /> REAL-TIME TAQQOSLASH</div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
        <div className="branch-comparison__legend">
          <span><i /> O‘rtacha natija</span>
          <span><GraduationCap size={14} /> O‘quvchilar soni nom ostida</span>
        </div>
      </div>

      <div className="branch-insight-grid">
        <div className="branch-insight branch-insight--winner">
          <span className="branch-insight__icon"><Medal size={18} /></span>
          <div><small>Eng yuqori natija</small><strong>{bestResult.name}</strong><b>{bestResult.average.toFixed(1)}%</b></div>
        </div>
        <div className="branch-insight">
          <span className="branch-insight__icon"><GraduationCap size={18} /></span>
          <div><small>Eng ko‘p o‘quvchi</small><strong>{mostStudents.name}</strong><b>{mostStudents.students} ta</b></div>
        </div>
        <div className="branch-insight">
          <span className="branch-insight__icon"><Building2 size={18} /></span>
          <div><small>Umumiy ko‘rsatkich</small><strong>{rows.length} ta filial</strong><b>{totalStudents} o‘quvchi</b></div>
        </div>
      </div>

      <div className="branch-chart-shell" style={{ height: chartHeight }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={rows}
            layout="vertical"
            margin={{ top: 8, right: 48, left: 18, bottom: 8 }}
            barCategoryGap="24%"
          >
            <defs>
              <linearGradient id="branchBarGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="var(--color-teal)" />
                <stop offset="58%" stopColor="var(--color-jungle)" />
                <stop offset="100%" stopColor="var(--color-olive)" />
              </linearGradient>
              <filter id="branchBarShadow" x="-10%" y="-50%" width="130%" height="200%">
                <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#086375" floodOpacity="0.18" />
              </filter>
            </defs>
            <CartesianGrid horizontal={false} strokeDasharray="4 6" stroke="var(--color-line)" />
            <XAxis
              type="number"
              domain={[0, 100]}
              tickCount={6}
              tickFormatter={(value) => `${value}%`}
              tick={{ fontSize: 10, fill: 'var(--color-muted)' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={118}
              axisLine={false}
              tickLine={false}
              tick={(props) => <BranchNameTick {...props} rows={rows} />}
            />
            <Tooltip content={<BranchTooltip />} cursor={{ fill: 'rgba(8,99,117,.045)' }} />
            <Bar
              dataKey="average"
              name="O‘rtacha natija"
              fill="url(#branchBarGradient)"
              radius={[0, 11, 11, 0]}
              minPointSize={4}
              isAnimationActive
              animationDuration={900}
              animationEasing="ease-out"
              style={{ filter: 'url(#branchBarShadow)' }}
            >
              <LabelList dataKey="average" content={<AverageLabel />} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
