import { admissionBannerMessage, type AdmissionDecision } from "../../lib/admissionLifecycleGate";

type Props = { decision: AdmissionDecision };

export function AdmissionOnlyBanner({ decision }: Props) {
  const message = admissionBannerMessage(decision);
  if (!message) return null;
  return (
    <div className="trisla-admission-only-banner" role="status">
      <strong>Admission lifecycle only</strong>
      <p className="trisla-muted">{message}</p>
    </div>
  );
}
