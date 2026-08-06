from __future__ import annotations
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer

# 1. Tìm đường dẫn tuyệt đối đến thư mục 'src'
src_path = Path(__file__).resolve().parent.parent / "src"

# 2. Chèn 'src' lên đầu danh sách tìm kiếm module của Python
sys.path.insert(0, str(src_path))

from pipelines.phase1 import main

if __name__ == "__main__":
    main()
