export default function StateSelect({
  options,
  value,
  onChange,
}: {
  options: string[];
  value: string[];
  onChange: (value: string[]) => void;
}) {
  return (
    <label>
      State
      <select
        value={value[0] ?? "All states"}
        onChange={(event) => onChange(event.target.value === "All states" ? [] : [event.target.value])}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
