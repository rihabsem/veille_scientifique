import { useLanguage } from "../i18n/LanguageContext";
import "./Spinner.css";

export default function Spinner({ label }) {
  const { t } = useLanguage();
  return (
    <div className="spinner-wrap" role="status">
      <span className="spinner" />
      <span>{label || t("common.loading")}</span>
    </div>
  );
}
