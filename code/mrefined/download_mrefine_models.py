#!/usr/bin/env python3
"""
Download and verify mReFinED models from HuggingFace

Usage:
    python download_mrefine_models.py --model base
    python download_mrefine_models.py --model large
    python download_mrefine_models.py --model both
    python download_mrefine_models.py --verify
"""

import os
import json
import argparse
from pathlib import Path
from typing import Optional

def download_mrefine_base():
    """Download microsoft/mrefine-d-base model"""
    print("=" * 60)
    print("Downloading: microsoft/mrefine-d-base")
    print("=" * 60)
    print("Size: ~440 MB")
    print("Time: ~2-3 minutes (depends on connection)")
    print()
    
    try:
        from transformers import CrossEncoder
        print("📥 Loading model from HuggingFace...")
        model = CrossEncoder('microsoft/mrefine-d-base')
        print("✅ Successfully downloaded mrefine-d-base")
        print(f"   Model saved to: {get_cache_dir()}/mrefine-d-base")
        return True
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        print("   Check internet connection and HuggingFace API access")
        return False


def download_mrefine_large():
    """Download microsoft/mrefine-d-large model"""
    print("=" * 60)
    print("Downloading: microsoft/mrefine-d-large")
    print("=" * 60)
    print("Size: ~1.3 GB")
    print("Time: ~5-7 minutes (depends on connection)")
    print()
    
    try:
        from transformers import CrossEncoder
        print("📥 Loading model from HuggingFace...")
        model = CrossEncoder('microsoft/mrefine-d-large')
        print("✅ Successfully downloaded mrefine-d-large")
        print(f"   Model saved to: {get_cache_dir()}/mrefine-d-large")
        return True
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        print("   Check internet connection and HuggingFace API access")
        return False


def get_cache_dir() -> str:
    """Get HuggingFace cache directory"""
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    return cache_dir


def verify_models() -> dict:
    """Verify if models are already downloaded"""
    print("=" * 60)
    print("Verifying downloaded models")
    print("=" * 60)
    print()
    
    cache_dir = get_cache_dir()
    results = {
        "base": False,
        "large": False,
        "cache_dir": cache_dir,
        "cache_exists": os.path.exists(cache_dir)
    }
    
    # Check base model
    base_pattern = "mrefine-d-base"
    if any(base_pattern in d for d in os.listdir(cache_dir) if os.path.isdir(os.path.join(cache_dir, d))):
        print(f"✅ {base_pattern}: DOWNLOADED")
        results["base"] = True
    else:
        print(f"❌ {base_pattern}: NOT FOUND")
    
    # Check large model
    large_pattern = "mrefine-d-large"
    if any(large_pattern in d for d in os.listdir(cache_dir) if os.path.isdir(os.path.join(cache_dir, d))):
        print(f"✅ {large_pattern}: DOWNLOADED")
        results["large"] = True
    else:
        print(f"❌ {large_pattern}: NOT FOUND")
    
    print()
    print(f"Cache directory: {cache_dir}")
    print(f"Models available: {sum([results['base'], results['large']])}/2")
    
    return results


def print_config_info():
    """Print mReFinED model configuration info"""
    print()
    print("=" * 60)
    print("mReFinED Model Configuration")
    print("=" * 60)
    print()
    
    # Load configs
    config_base_path = Path(__file__).parent / "config_mrefine_base.json"
    config_large_path = Path(__file__).parent / "config_mrefine_large.json"
    
    if config_base_path.exists():
        with open(config_base_path) as f:
            config_base = json.load(f)
        print("📋 Base Model Configuration:")
        print(f"   Model: {config_base['model_name']}")
        print(f"   Size: {config_base['model_size_mb']} MB")
        print(f"   Languages: {len(config_base['languages_supported'])} languages")
        print(f"   Speed: {config_base['speed_ranking']}")
        print(f"   Accuracy: {config_base['accuracy_ranking']}")
        print()
    
    if config_large_path.exists():
        with open(config_large_path) as f:
            config_large = json.load(f)
        print("📋 Large Model Configuration:")
        print(f"   Model: {config_large['model_name']}")
        print(f"   Size: {config_large['model_size_mb']} MB")
        print(f"   Languages: {len(config_large['languages_supported'])} languages")
        print(f"   Speed: {config_large['speed_ranking']} ({config_large['speed_multiplier']}x slower)")
        print(f"   Accuracy: {config_large['accuracy_ranking']} (+{config_large['accuracy_improvement']})")
        print()


def print_usage_examples():
    """Print usage examples"""
    print()
    print("=" * 60)
    print("Usage Examples")
    print("=" * 60)
    print()
    
    print("Python (Auto-download on first use):")
    print("  from transformers import CrossEncoder")
    print("  model = CrossEncoder('microsoft/mrefine-d-base')")
    print("  # Auto-downloads if not in cache")
    print()
    
    print("Direct download (this script):")
    print("  python download_mrefine_models.py --model base")
    print("  python download_mrefine_models.py --model large")
    print("  python download_mrefine_models.py --model both")
    print()
    
    print("Verify downloaded models:")
    print("  python download_mrefine_models.py --verify")
    print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Download and manage mReFinED models from HuggingFace"
    )
    parser.add_argument(
        "--model",
        choices=["base", "large", "both"],
        default="base",
        help="Which model to download"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify downloaded models only"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show configuration info"
    )
    
    args = parser.parse_args()
    
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  mReFinED Model Manager".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Show info if requested
    if args.info:
        print_config_info()
        print_usage_examples()
        return
    
    # Verify if requested
    if args.verify:
        results = verify_models()
        if results["base"] or results["large"]:
            print("✅ At least one model is available")
        else:
            print("ℹ️  No models downloaded yet. Run with --model to download")
        return
    
    # Download models
    success = True
    if args.model in ["base", "both"]:
        if not download_mrefine_base():
            success = False
    
    if args.model in ["large", "both"]:
        print()
        if not download_mrefine_large():
            success = False
    
    # Show summary
    print()
    print("=" * 60)
    print("Download Summary")
    print("=" * 60)
    results = verify_models()
    
    if success:
        print()
        print("✅ Download completed successfully!")
        print()
        print("Next steps:")
        print("  1. Models are cached and ready to use")
        print("  2. Run evaluation scripts to test models")
        print("  3. See MREFINE_MODELS_README.md for usage")
    else:
        print()
        print("❌ Some downloads failed. Check errors above.")
    
    print()


if __name__ == "__main__":
    main()
