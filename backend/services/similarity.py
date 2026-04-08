"""
SimHash-based copy-paste detection.
Dùng datasketch để tính SimHash cho review text.
"""

from datasketch import MinHash
import re


def _tokenize(text: str) -> list[str]:
    """Normalize và tokenize text thành list of shingles (3-gram)."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    tokens = text.split()
    if len(tokens) < 3:
        return tokens
    return [" ".join(tokens[i:i+3]) for i in range(len(tokens) - 2)]


def compute_simhash(text: str, num_perm: int = 128) -> int:
    """
    Tính SimHash (dạng int) cho text.
    Lưu vào DB column simhash (BIGINT).
    """
    m = MinHash(num_perm=num_perm)
    shingles = _tokenize(text)
    if not shingles:
        return 0
    for s in shingles:
        m.update(s.encode("utf-8"))
    # Dùng hashvalue[0] làm fingerprint đại diện
    return int(m.hashvalues[0])


def compute_minhash(text: str, num_perm: int = 128) -> MinHash:
    """Trả về MinHash object để so sánh Jaccard similarity."""
    m = MinHash(num_perm=num_perm)
    shingles = _tokenize(text)
    for s in shingles:
        m.update(s.encode("utf-8"))
    return m


def jaccard_similarity(text1: str, text2: str, num_perm: int = 128) -> float:
    """
    Tính Jaccard similarity giữa 2 văn bản.
    Return: 0.0–1.0
    """
    m1 = compute_minhash(text1, num_perm)
    m2 = compute_minhash(text2, num_perm)
    return m1.jaccard(m2)


def find_duplicate_similarity(
    target_text: str, batch_texts: list[str], num_perm: int = 128
) -> tuple[float, int]:
    """
    So sánh target_text với tất cả texts trong batch.

    Returns:
        max_similarity: float — similarity cao nhất tìm được
        match_count: int — số texts có similarity > 0.7
    """
    if not batch_texts:
        return 0.0, 0

    target_mh = compute_minhash(target_text, num_perm)
    max_sim = 0.0
    match_count = 0

    for text in batch_texts:
        sim = target_mh.jaccard(compute_minhash(text, num_perm))
        if sim > max_sim:
            max_sim = sim
        if sim > 0.7:
            match_count += 1

    return max_sim, match_count


def find_clusters(
    texts: list[str],
    review_ids: list[int],
    threshold: float = 0.8,
    num_perm: int = 128,
) -> list[list[int]]:
    """
    Gom nhóm reviews có similarity > threshold.
    Trả về list các cluster (mỗi cluster là list review_id).
    Chỉ trả cluster có ≥ 2 members.
    """
    n = len(texts)
    if n == 0:
        return []

    minhashes = [compute_minhash(t, num_perm) for t in texts]
    visited = [False] * n
    clusters: list[list[int]] = []

    for i in range(n):
        if visited[i]:
            continue
        cluster = [review_ids[i]]
        visited[i] = True
        for j in range(i + 1, n):
            if visited[j]:
                continue
            sim = minhashes[i].jaccard(minhashes[j])
            if sim >= threshold:
                cluster.append(review_ids[j])
                visited[j] = True
        if len(cluster) >= 2:
            clusters.append(cluster)

    return clusters
