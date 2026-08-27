'use client';

type StateOption = { value: string; label: string };

export default function MultiStateSelect({
  values,
  options,
  onChange,
  allLabel = 'All locations',
  className = '',
}: {
  values: string[];
  options: StateOption[];
  onChange: (values: string[]) => void;
  allLabel?: string;
  className?: string;
}) {
  const selected = new Set(values);
  const summary = values.length === 0
    ? allLabel
    : values.length <= 2
      ? values.map((value) => options.find((option) => option.value === value)?.label || value).join(', ')
      : `${values.length} locations selected`;

  function toggle(value: string) {
    onChange(selected.has(value)
      ? values.filter((item) => item !== value)
      : [...values, value]);
  }

  return (
    <details className={`multi-select ${className}`.trim()}>
      <summary>{summary}</summary>
      <div className="multi-select-menu">
        <button type="button" onClick={() => onChange([])}>Any location</button>
        {options.map((option) => (
          <label key={option.value}>
            <input
              type="checkbox"
              checked={selected.has(option.value)}
              onChange={() => toggle(option.value)}
            />
            <span>{option.label}</span>
          </label>
        ))}
      </div>
    </details>
  );
}
