interface Option<T extends string | number> {
  value: T;
  label: string;
  hint?: string;
  icon?: string;
}

interface ChoiceGroupProps<T extends string | number> {
  legend: string;
  name: string;
  options: Option<T>[];
  value: T | null;
  onChange: (value: T) => void;
  /** "grid" puts short options side by side; "list" stacks long ones. */
  layout?: "grid" | "list";
}

/**
 * A group of big tappable choices built on real radio buttons,
 * so arrow keys, focus and screen readers work without extra code.
 */
export function ChoiceGroup<T extends string | number>({
  legend,
  name,
  options,
  value,
  onChange,
  layout = "list",
}: ChoiceGroupProps<T>) {
  return (
    <fieldset className="choices">
      <legend className="choices__legend">{legend}</legend>
      <div className={layout === "grid" ? "choices__grid" : "choices__list"}>
        {options.map((option) => (
          <label className="choice" key={option.value}>
            <input
              className="choice__input"
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
            />
            <span className="choice__card">
              {option.icon && <span className="choice__icon" aria-hidden="true">{option.icon}</span>}
              <span className="choice__label">{option.label}</span>
              {option.hint && <span className="choice__hint">{option.hint}</span>}
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
