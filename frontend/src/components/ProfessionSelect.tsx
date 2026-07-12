export default function ProfessionSelect({
  options,
  value,
  onChange,
}: {
  options: Array<{ id: number; socCode: string; socTitle: string }>;
  value: number[];
  onChange: (value: number[]) => void;
}) {
  return (
    <label>
      IT profession
      <select
        value={value[0] ?? ""}
        onChange={(event) => onChange(event.target.value ? [Number(event.target.value)] : [])}
      >
        <option value="">All IT professions</option>
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.socTitle} ({option.socCode})
          </option>
        ))}
      </select>
    </label>
  );
}
