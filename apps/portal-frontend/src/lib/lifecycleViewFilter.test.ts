/**
 * lifecycleViewFilter tests — run: npx tsx src/lib/lifecycleViewFilter.test.ts
 */
import {
  isRuntimeLifecycleNavVisible,
  lifecycleViewFromParam,
  showLifecycleSectionInView,
} from "./lifecycleViewFilter";

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

assert(lifecycleViewFromParam(null) === "admission", "default admission view");
assert(lifecycleViewFromParam("runtime") === "runtime", "runtime view param");

assert(isRuntimeLifecycleNavVisible("ACCEPT"), "nav visible accept");
assert(!isRuntimeLifecycleNavVisible("REJECT"), "nav hidden reject");
assert(!isRuntimeLifecycleNavVisible("RENEGOTIATE"), "nav hidden reneg");
assert(isRuntimeLifecycleNavVisible(null), "nav visible when unknown");

assert(
  showLifecycleSectionInView("runtimeAssurance", "ACCEPT", "runtime"),
  "assurance in runtime view accept",
);
assert(
  !showLifecycleSectionInView("runtimeAssurance", "ACCEPT", "admission"),
  "assurance not in admission view accept",
);
assert(
  showLifecycleSectionInView("decisionEvidence", "ACCEPT", "admission"),
  "evidence in admission view",
);
assert(
  !showLifecycleSectionInView("governance", "ACCEPT", "admission"),
  "governance hidden admission accept",
);
assert(
  showLifecycleSectionInView("governance", "REJECT", "admission"),
  "governance admission reject",
);
assert(
  !showLifecycleSectionInView("runtimeSnapshot", "REJECT", "runtime"),
  "no snapshot reject runtime view",
);

console.log("lifecycleViewFilter.test.ts: OK");
