import json
import csv
import transformers
import torch
import re
from tqdm import tqdm
import os
import argparse


def resolve_hf_token(cli_token: str) -> str:
    """Resolve a Hugging Face token without encouraging CLI token usage.

    Prefer env vars so tokens don't end up in shell history/process listings.
    """

    if cli_token:
        return cli_token

    return (
        os.environ.get("HUGGINGFACE_HUB_TOKEN")
        or os.environ.get("HF_TOKEN")
        or os.environ.get("HUGGINGFACE_TOKEN")
        or ""
    )


def process_candidates(candidates, n_candidates):
    output = []
    for item in candidates[:min(n_candidates, len(candidates))]:
        output.append({
            "wikipedia_page": item["label"],
            "wikidata_id": item["wb_id"],
            "type": item["type"],
            "descr":item["descr"],
            "date": item["min_date"],
        })
    return output


def main():
    parser = argparse.ArgumentParser(description="LLM Prompting for Entity Disambiguation from Candidate List")
    parser.add_argument("--json_f", type=str, required=True, help="Path to JSON list of candidates")
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to dataset directory")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for results")
    parser.add_argument("--threshold", type=float, default=0, help="Threshold to be used to filter hard negatives.")
    parser.add_argument("--model_id", type=str, default="mistralai/Mistral-Small-24B-Instruct-2501", help="Huggingface repo of LLM")
    parser.add_argument(
        "--hf_token",
        type=str,
        default="",
        help=(
            "Hugging Face token (discouraged: can leak via shell history). "
            "Prefer env var HUGGINGFACE_HUB_TOKEN or 'huggingface-cli login'."
        ),
    )
    parser.add_argument("--n_candidates", type=int, default=50, help="Number of candidates to put in prompt.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing output.csv in output_dir (skips already processed doc_id+start_pos).",
    )

    args = parser.parse_args()
    with open(args.json_f, "r", encoding="utf-8") as f:
        retriever_results = json.load(f)

    with open(os.path.join(args.dataset_path, "paragraphs_test.csv", ), "r", encoding="utf-8") as f:
        paragraphs = list(csv.DictReader(f))

    iso_to_lang = {"en":"English", "it":"Italian", "fr":"French", "sv":"Swedish", "de":"German", "fi":"Finnish",
                   "nl":"Dutch"}

    hf_token = resolve_hf_token(args.hf_token)

    # Optional memory caps to coexist with other GPU jobs.
    # Example:
    #   export MHEL_MAX_GPU_MEM="20GiB"
    #   export MHEL_MAX_CPU_MEM="120GiB"
    max_gpu_mem = os.environ.get("MHEL_MAX_GPU_MEM", "").strip()
    max_cpu_mem = os.environ.get("MHEL_MAX_CPU_MEM", "").strip()
    max_memory = None
    if max_gpu_mem or max_cpu_mem:
        max_memory = {}
        if max_gpu_mem:
            max_memory[0] = max_gpu_mem
        if max_cpu_mem:
            max_memory["cpu"] = max_cpu_mem

    pipeline = transformers.pipeline(
        "text-generation",
        model=args.model_id,
        model_kwargs={
            "torch_dtype": torch.bfloat16,
            **({"max_memory": max_memory} if max_memory else {}),
        },
        device_map="auto",
        token=hf_token or None,
    )


    system_prompt1 = """
    You are a highly precise multilingual information extraction system specialized in disambiguating entities within noisy historical texts.
    Your task is to analyse the text provided by the user and determine if the reference marked by [ENT] tags can be associated or not to one of the candidate Wikidata entities provided in the JSON list.
    Always respond by saying either "yes" or "no". Do not generate Python code.
    """
    
    system_prompt2 = """
    You are an effective multilingual information extraction system specialized in disambiguating entities within noisy 
    historical texts.
    Your task is to analyse the text provided by the user and disambiguate the reference marked by [ENT] tags by 
    selecting a Wikidata entity from a given list of candidates.
    Always respond by returning a JSON-formatted answer; do not generate Python code.
    """

    os.makedirs(args.output_dir, exist_ok=True)

    fieldnames = [
        "doc_id",
        "start_pos",
        "end_pos",
        "surface",
        "gt_id",
        "type",
        "identifier",
        "title",
        "answer",
        "score",
    ]
    output_csv_path = os.path.join(args.output_dir, "output.csv")

    processed_keys = set()
    if args.resume and os.path.exists(output_csv_path):
        try:
            with open(output_csv_path, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    processed_keys.add((row.get("doc_id"), str(row.get("start_pos")).strip()))
            print(f"Resume enabled: loaded {len(processed_keys)} completed rows from {output_csv_path}")
        except Exception as e:
            print(f"Warning: could not read existing output.csv for resume ({e}); starting fresh")

    write_header = not os.path.exists(output_csv_path)
    out_f = open(output_csv_path, "a", encoding="utf-8", newline="")
    writer = csv.DictWriter(out_f, fieldnames=fieldnames)
    if write_header:
        writer.writeheader()
        out_f.flush()
    paragraphs_dict = {p["doc_id"]: p for p in paragraphs}

    for item in tqdm(retriever_results):
        doc_id = item["doc_id"]
        start_pos = int(item["start_pos"])
        end_pos = int(item["end_pos"])
        key = (doc_id, str(start_pos))
        if args.resume and key in processed_keys:
            continue

        if args.threshold > 0 and item["candidates"][0]["score"] >= args.threshold:
            row_out = {
                "doc_id":doc_id,
                "start_pos":start_pos,
                "end_pos":end_pos,
                "surface":item["surface"],
                "gt_id": item["identifier"],
                "type":item["type"],
                "identifier":item["candidates"][0]["wb_id"],
                "title":item["candidates"][0]["label"],
                "answer":"",
                "score":item["candidates"][0]["score"]
            }
            writer.writerow(row_out)
            out_f.flush()
            processed_keys.add(key)
        else:
            paragraph = paragraphs_dict[doc_id]
            date = paragraph["publication_date"]
            lang = iso_to_lang[paragraph["lang"]]
            genre = paragraph["genre"]
            text = paragraph["text"]
            processed_text = text[max(0, start_pos - 500):start_pos] + "[ENT] " + text[start_pos:end_pos] + " [ENT] " +text[end_pos:min(len(text), end_pos + 500)]
            processed_candidates = process_candidates(item["candidates"], args.n_candidates)
            allowed_qids = set([cand["wikidata_id"].upper() for cand in processed_candidates])
            processed_candidates_json = json.dumps(processed_candidates, ensure_ascii=False, indent=2)
            user_prompt1 = """
            Read the input text extracted from """ + lang + " " + genre + " published in " + date + """.
            Answer if the entity mentioned between the [ENT] tags in the input text corresponds to one of the candidate Wikidata entity provided in the json.
            Give a simple binary answer.
            ---------------------
            Input Text:
            """ + processed_text + """
            ---------------------
            JSON List of Candidates:
            ```json
            """ + processed_candidates_json + """ 
            ``` ."""
            messages = [
                {"role": "system", "content": system_prompt1},
                {"role": "user", "content": user_prompt1},
            ]

            outputs = pipeline(
                messages,
                max_new_tokens=128,
            )
            response = outputs[0]["generated_text"][-1]["content"]
            if "yes" in response.lower():
                user_prompt2 = """
                Read the input text extracted from """ + lang + " " + genre + " published in " + date + """.
                Disambiguate the entity mentioned between the [ENT] tags by selecting the most appropriate Wikidata entity from a given list of candidates.    
                Return the corresponding Wikipedia page title and Wikidata ID of the selected entity in a JSON object formatted as follows:
            
                ```json
                {"wikipedia_page":"", "wikidata_id":""}
                ```
            
                Make sure to select both the Wikidata ID and the Wikipedia page title from the provided list of candidates. 
                Pay attention that the list of candidates may not include the entity mentioned. If none of the candidates match with high confidence the entity tagged with [ENT], return an empty json.

                ---------------------
                Input Text:
                """ + processed_text + """
                ---------------------
                JSON List of Candidates:
                ```json
                """ + processed_candidates_json + """ 
                ``` ."""
                messages = [
                {"role": "system", "content": system_prompt2},
                {"role": "user", "content": user_prompt2},
                ]

                outputs = pipeline(
                    messages,
                    max_new_tokens=256,
                )

                response = outputs[0]["generated_text"][-1]["content"]
                match = re.search(r'"wikidata_id"\s*:\s*"(Q\d+)"', response)
                if match and match.group(1).upper() in allowed_qids:
                    wikidata_id = match.group(1).upper()
                    selected_entity = [
                        x for x in item["candidates"] if (x.get("wb_id") or "").upper() == wikidata_id
                    ][0]
                    row_out = {
                        "doc_id":doc_id,
                        "start_pos":start_pos,
                        "end_pos":end_pos,
                        "surface":item["surface"],
                        "gt_id": item["identifier"],
                        "type":item["type"],
                        "identifier":wikidata_id,
                        "title":selected_entity["label"],
                        "answer":re.sub(r'\s+', " ", response),
                        "score":selected_entity["score"]
                    }
                    writer.writerow(row_out)
                    out_f.flush()
                    processed_keys.add(key)

                else:
                    row_out = {
                    "doc_id": doc_id,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "surface": item["surface"],
                    "gt_id": item["identifier"],
                    "type": item["type"],
                    "identifier": "NIL",
                    "title": item["surface"],
                    "answer": re.sub(r'\s+', " ", response),
                    "score": 0
                    }
                    writer.writerow(row_out)
                    out_f.flush()
                    processed_keys.add(key)
            
            else:
                row_out = {
                    "doc_id": doc_id,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "surface": item["surface"],
                    "gt_id": item["identifier"],
                    "type": item["type"],
                    "identifier": "NIL",
                    "title": item["surface"],
                    "answer": re.sub(r'\s+', " ", response),
                    "score": 0
                    }
                writer.writerow(row_out)
                out_f.flush()
                processed_keys.add(key)
        
    out_f.close()
    print(f"Processed total items: {len(retriever_results)}")
    print(f"Wrote rows (unique keys): {len(processed_keys)}")

if __name__ == "__main__":
    main()


