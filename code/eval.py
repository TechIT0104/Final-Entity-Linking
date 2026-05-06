import os
import csv
import argparse


# Example commands:
# path_data = "../test_data/HIPE_EN"
# path_results = "../results/hipe_en"


def _norm_id(raw_id: str) -> str:
    raw_id = (raw_id or "").strip()
    return raw_id if raw_id.upper().startswith("Q") else "NIL"


def _norm_pos(raw_pos) -> str:
    """Normalize start/end positions for stable joins across CSVs."""

    if raw_pos is None:
        return ""
    s = str(raw_pos).strip()
    if s == "":
        return ""
    try:
        # some CSV writers may emit floats like "123.0"
        return str(int(float(s)))
    except Exception:
        return s


def eval_ed(data, predictions):
    """Compute micro P/R/F1 for entity disambiguation.

    With exactly one prediction per gold mention, micro P=R=F1=accuracy.
    This implementation also handles missing/extra predictions robustly.
    """

    gold_by_key = {}
    for row in data:
        key = (row.get("doc_id"), _norm_pos(row.get("start_pos")))
        gold_by_key[key] = _norm_id(row.get("identifier", ""))

    pred_by_key = {}
    pred_row_by_key = {}
    for row in predictions:
        key = (row.get("doc_id"), _norm_pos(row.get("start_pos")))
        pred_by_key[key] = _norm_id(row.get("identifier", ""))
        pred_row_by_key[key] = row

    tp_rows = []
    fp_rows = []
    fn_rows = []

    tp = fp = fn = 0

    for gold_row in data:
        key = (gold_row.get("doc_id"), _norm_pos(gold_row.get("start_pos")))
        gold_id = gold_by_key[key]
        if key not in pred_by_key:
            fn += 1
            fn_rows.append(gold_row)
            continue

        pred_id = pred_by_key[key]
        if pred_id == gold_id:
            tp += 1
            # keep the prediction row in TP for easier inspection
            tp_rows.append(pred_row_by_key.get(key, gold_row))
        else:
            fp += 1
            fn += 1
            fp_rows.append(pred_row_by_key.get(key, {"doc_id": key[0], "start_pos": key[1], "identifier": pred_id}))
            fn_rows.append(gold_row)

    # Extra predictions (should be rare)
    for pred_row in predictions:
        key = (pred_row.get("doc_id"), str(pred_row.get("start_pos")))
        if key not in gold_by_key:
            fp += 1
            fp_rows.append(pred_row)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    accuracy = tp / len(gold_by_key) if gold_by_key else 0.0

    return tp_rows, fp_rows, fn_rows, precision, recall, f1, accuracy


def main():
    parser = argparse.ArgumentParser(description="Script for computing micro averaged accuracy in Entity Disambiguation")
    parser.add_argument("--path_results", type=str, required=True, help="Path to JSON list of candidates")
    parser.add_argument("--path_data", type=str, required=True, help="Path to dataset directory")
    args = parser.parse_args()

    with open(os.path.join(args.path_results, "output.csv"), "r", encoding="utf-8") as f1:
        predictions = list(csv.DictReader(f1, delimiter=","))

    with open(os.path.join(args.path_data, "annotations_test.csv"), "r", encoding="utf-8") as f2:
        data = list(csv.DictReader(f2, delimiter=","))

    tp, fp, fn, precision, recall, f1, accuracy = eval_ed(data, predictions)

    with open(os.path.join(args.path_results, "result.txt"), "w") as output:
        output.write("True Positives: " + str(len(tp)) + "\n\n")
        output.write("False Positives: " + str(len(fp)) + "\n\n")
        output.write("False Negatives: " + str(len(fn)) + "\n\n")
        output.write("Precision: " + str(precision) + "\n\n")
        output.write("Recall: " + str(recall) + "\n\n")
        output.write("F1: " + str(f1) + "\n\n")
        output.write("Accuracy: " + str(accuracy) + "\n\n")

    p_keys = tp[0].keys() if tp else []
    fp_keys = fp[0].keys() if fp else []
    n_keys = fn[0].keys() if fn else []

    if tp:
        tp_file = open(os.path.join(args.path_results, "tp_ed.csv"), "w", encoding="utf-8", newline="")
        dict_writer = csv.DictWriter(tp_file, p_keys)
        dict_writer.writeheader()
        dict_writer.writerows(tp)
        tp_file.close()

    if fp:
        fp_file = open(os.path.join(args.path_results, "fp_ed.csv"), "w", encoding="utf-8", newline="")
        dict_writer = csv.DictWriter(fp_file, fp_keys)
        dict_writer.writeheader()
        dict_writer.writerows(fp)
        fp_file.close()

    if fn:
        fn_file = open(os.path.join(args.path_results, "fn_ed.csv"), "w", encoding="utf-8", newline="")
        dict_writer = csv.DictWriter(fn_file, n_keys)
        dict_writer.writeheader()
        dict_writer.writerows(fn)
        fn_file.close()



if __name__ == "__main__":
    main()