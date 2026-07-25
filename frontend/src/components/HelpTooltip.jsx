import { useState } from "react";
import { HelpIcon } from "./icons";
import { useLanguage } from "../i18n/LanguageContext";
import "./HelpTooltip.css";

export default function HelpTooltip({ text }) {
  const { t } = useLanguage();
  const [open, setOpen] = useState(false);

  return (
    <span
      className="help-tooltip"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      <button
        type="button"
        className="help-tooltip__trigger"
        aria-label={t("common.help")}
        aria-expanded={open}
        onClick={() => setOpen((prev) => !prev)}
      >
        <HelpIcon width={14} height={14} />
      </button>
      {open && (
        <span className="help-tooltip__bubble" role="tooltip">
          {text}
        </span>
      )}
    </span>
  );
}
