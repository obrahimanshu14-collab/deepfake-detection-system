# Accuracy improvement workflow

The project separates model deployment from model QA. Run `evaluate_test.py` against the held-out test split after every model change.

Recommended experiment order:

1. Establish the current held-out baseline with `evaluate_test.py`.
2. Audit duplicate and near-duplicate leakage before trusting accuracy.
3. Train with multiple dataset fractions: 8%, 25%, 50%, and 100%.
4. Compare 160px, 224px, and compression-robust preprocessing.
5. Benchmark MobileNetV2 against a stronger backbone before changing the production checkpoint.
6. Tune classification thresholds on validation data only, then report final results once on the held-out test set.
7. Evaluate on an external set containing unseen generators, codecs, resolutions, and talking-avatar content.

Never select a production model using the held-out test split. Use validation data for model selection and reserve the test set for final reporting.
