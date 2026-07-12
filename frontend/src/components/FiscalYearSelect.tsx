export default function FiscalYearSelect({
  options,
  value,
  onChange,
}: {
  options: Array<{ label: string; value: string | number; reportingPeriod: string | null }>;
  value: number[];
  onChange: (value: number[]) => void;
}) {
  return (
    <label>
      Fiscal year
      <select
        value={value[0] ?? "all"}
        onChange={(event) => {
          const next = event.target.value;
          onChange(next === "all" ? [] : [Number(next)]);
        }}
      >
        {options.map((option) => (
          <option key={`${option.value}`} value={option.value}>
            {option.reportingPeriod ? `${option.label} - ${option.reportingPeriod}` : option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
