from dataclasses import dataclass, Field


@dataclass
class AnomalyLimits:
    min: float
    max: float

    def is_in_range(self, val):
        return val > self.min and val < self.max


@dataclass
class AnomalyDetection:
    """Detect anomalous values in a record based on limits."""

    input_field: str
    limits: AnomalyLimits
    output_field: str
    include_status: bool = False

    def run(self, record_groups):
        # Sadly, dataclass doesn't handle nesting so we must convert
        # from the original dictionary.
        self.limits = AnomalyLimits(**self.limits)

        for group in record_groups:
            for rec in group["records"]:
                val = rec[self.input_field]
                if not self.limits.is_in_range(val):
                    rec[self.output_field] = True
                    if self.include_status:
                        rec["status"] = "alert"
            yield group
