"""Phase 2 sequence parsing, validation, and composition analysis service.

Uses Biopython (`Bio.SeqIO`, `Bio.Seq.Seq`, and `Bio.SeqUtils.molecular_weight`)
when installed, with a spec-identical fallback when running inside a minimal container.
"""
from io import StringIO
from typing import Dict, List, Optional, Tuple

from app.config import get_settings
from app.errors import AppError
from app.schemas import AnalyzeResponse, BaseCounts, FastaRecordMeta, GcWindowPoint

try:
    from Bio import SeqIO  # type: ignore
    from Bio.Seq import Seq  # type: ignore
    from Bio.SeqUtils import molecular_weight as bio_molecular_weight  # type: ignore

    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

ALLOWED_DNA_BASES = frozenset(("A", "T", "G", "C", "N"))
COMPLEMENT_TABLE = str.maketrans({"A": "T", "T": "A", "G": "C", "C": "G", "N": "N"})

# Exact Biopython Bio.Data.IUPACData.unambiguous_dna_weights (anhydrous monophosphate residues in ssDNA)
# Biopython molecular_weight(seq, "DNA") sums residue weights and subtracts 61.96 Da (5'-monophosphate vs triphosphate/terminal OH adjustment)
_BIOPYTHON_DNA_WEIGHTS: Dict[str, float] = {
    "A": 313.209,
    "T": 304.196,
    "G": 329.208,
    "C": 289.184,
}
_BIOPYTHON_TERMINAL_CORRECTION = -61.96


def parse_fasta_or_raw(raw_text: str) -> List[Tuple[str, str, str]]:
    """Parse FASTA text (single or multi-record) or plain sequence string.

    Returns a list of tuples: (record_id, description, raw_sequence_lines_joined).
    """
    if not raw_text or not raw_text.strip():
        raise AppError(
            code="EMPTY_SEQUENCE",
            message="Sequence input is empty. Upload a FASTA file or paste a DNA sequence containing A, T, G, C, or N.",
            status_code=400,
        )

    settings = get_settings()
    if len(raw_text.encode("utf-8")) > settings.max_file_size_bytes:
        raise AppError(
            code="FILE_TOO_LARGE",
            message="File exceeds the 5 MB limit. Upload a FASTA file smaller than 5 MB.",
            status_code=413,
        )

    stripped = raw_text.lstrip()
    if stripped.startswith(">"):
        records: List[Tuple[str, str, str]] = []
        if HAS_BIOPYTHON:
            for rec in SeqIO.parse(StringIO(stripped), "fasta"):
                records.append((rec.id or "record", rec.description or rec.id, str(rec.seq)))
        else:
            current_id: Optional[str] = None
            current_desc: str = ""
            seq_Parts: List[str] = []
            for line in stripped.splitlines():
                line_s = line.strip()
                if not line_s:
                    continue
                if line_s.startswith(">"):
                    if current_id is not None:
                        records.append((current_id, current_desc, "".join(seq_Parts)))
                    header = line_s[1:].strip()
                    parts = header.split(None, 1)
                    current_id = parts[0] if parts else f"record_{len(records) + 1}"
                    current_desc = header
                    seq_Parts = []
                else:
                    seq_Parts.append(line_s)
            if current_id is not None:
                records.append((current_id, current_desc, "".join(seq_Parts)))

        if not records:
            raise AppError(
                code="EMPTY_FASTA",
                message="No FASTA records found. Ensure the file begins with a '>header' line followed by a DNA sequence.",
                status_code=400,
            )
        return records

    # Plain pasted sequence without a '>' FASTA header
    return [("seq_1", "Pasted DNA sequence", stripped)]


def clean_and_validate_dna(raw_seq: str) -> str:
    """Uppercase sequence, strip all whitespace/newlines, and validate A, T, G, C, N.

    - If 'U' is found, tells the user the sequence looks like RNA and shows the 1-based position.
    - If any other invalid character is found, names the first invalid character and its 1-based position.
    - Rejects sequences above 100,000 bp in V1 with a friendly message.
    """
    cleaned = "".join(raw_seq.split()).upper()
    if not cleaned:
        raise AppError(
            code="EMPTY_SEQUENCE",
            message="Sequence contains no nucleotides. Provide a DNA sequence with A, T, G, C, or N.",
            status_code=400,
        )

    settings = get_settings()
    if len(cleaned) > settings.max_sequence_length_bp:
        raise AppError(
            code="SEQUENCE_TOO_LONG",
            message=(
                f"Sequence length ({len(cleaned):,} bp) exceeds the V1 maximum of "
                f"{settings.max_sequence_length_bp:,} bp. Trim the sequence to 100,000 bp or fewer."
            ),
            status_code=400,
        )

    for idx, ch in enumerate(cleaned):
        if ch not in ALLOWED_DNA_BASES:
            pos_1based = idx + 1
            if ch == "U":
                raise AppError(
                    code="RNA_DETECTED",
                    message=(
                        f"Character 'U' at position {pos_1based} indicates this sequence looks like RNA. "
                        "Convert U to T to analyze DNA."
                    ),
                    status_code=400,
                )
            raise AppError(
                code="INVALID_BASE",
                message=(
                    f"Invalid character '{ch}' at position {pos_1based}. "
                    "Only A, T, G, C, and N are allowed."
                ),
                status_code=400,
            )

    return cleaned


def compute_molecular_weight_ssdna(cleaned_seq: str) -> Tuple[float, str]:
    """Compute single-stranded DNA molecular weight in Daltons.

    Biopython's `molecular_weight(seq, 'DNA')` raises a ValueError on ambiguous 'N' bases
    because 'N' has no single fixed atomic mass. We explicitly exclude 'N' bases before
    calling `molecular_weight(unambiguous_seq, 'DNA')` and state how many N bases were excluded.
    """
    n_count = cleaned_seq.count("N")
    unambiguous = cleaned_seq.replace("N", "") if n_count > 0 else cleaned_seq

    if not unambiguous:
        return 0.0, f"All {n_count} bases are N; unambiguous molecular weight is 0.0 Da (N bases excluded)."

    if HAS_BIOPYTHON:
        mw = float(bio_molecular_weight(Seq(unambiguous), "DNA"))
    else:
        mw = (
            sum(_BIOPYTHON_DNA_WEIGHTS[b] for b in unambiguous)
            + _BIOPYTHON_TERMINAL_CORRECTION
        )

    mw_rounded = round(mw, 2)
    if n_count > 0:
        note = f"Computed over {len(unambiguous):,} unambiguous bases ({n_count:,} N bases excluded)."
    else:
        note = f"Computed over all {len(unambiguous):,} unambiguous single-stranded DNA bases."
    return mw_rounded, note


def compute_sliding_gc_profile(cleaned_seq: str, window_size: int = 100) -> List[GcWindowPoint]:
    """Compute GC% along the sequence using a sliding window (default 100 bp)."""
    length = len(cleaned_seq)
    if length == 0:
        return []

    effective_win = min(window_size, length)
    # Keep payload compact (~60 points max) while exact at 100 bp window
    step = max(1, (length - effective_win) // 50) if length > effective_win else 1

    points: List[GcWindowPoint] = []
    pos = 0
    while pos <= length - effective_win:
        window = cleaned_seq[pos : pos + effective_win]
        g_c = window.count("G") + window.count("C")
        non_n = len(window) - window.count("N")
        gc_pct = round((g_c / non_n) * 100.0, 2) if non_n > 0 else 0.0
        points.append(GcWindowPoint(position=pos + 1, gc_percent=gc_pct))
        if length == effective_win:
            break
        pos += step

    return points


def analyze_dna_input(
    raw_input: str,
    requested_id: Optional[str] = None,
    include_complements: bool = False,
    gc_window_size: int = 100,
) -> AnalyzeResponse:
    """Parse, validate, and analyze a FASTA or raw DNA sequence string."""
    raw_records = parse_fasta_or_raw(raw_input)

    # Validate all records and collect metadata for multi-record dropdown
    validated_records: List[Tuple[str, str, str]] = []
    record_metas: List[FastaRecordMeta] = []

    for rec_id, rec_desc, rec_raw_seq in raw_records:
        cleaned = clean_and_validate_dna(rec_raw_seq)
        validated_records.append((rec_id, rec_desc, cleaned))
        record_metas.append(
            FastaRecordMeta(id=rec_id, description=rec_desc, length=len(cleaned))
        )

    selected = validated_records[0]
    if requested_id:
        for candidate in validated_records:
            if candidate[0] == requested_id:
                selected = candidate
                break

    seq_id, seq_desc, seq = selected
    length = len(seq)

    a_count = seq.count("A")
    t_count = seq.count("T")
    g_count = seq.count("G")
    c_count = seq.count("C")
    n_count = seq.count("N")

    non_n_total = a_count + t_count + g_count + c_count
    if non_n_total > 0:
        gc_percent = round(((g_count + c_count) / non_n_total) * 100.0, 2)
        at_percent = round(((a_count + t_count) / non_n_total) * 100.0, 2)
    else:
        gc_percent = 0.0
        at_percent = 0.0

    mw_da, mw_note = compute_molecular_weight_ssdna(seq)
    gc_profile = compute_sliding_gc_profile(seq, window_size=gc_window_size)

    complement_str: Optional[str] = None
    rev_complement_str: Optional[str] = None
    if include_complements:
        if HAS_BIOPYTHON:
            bio_seq = Seq(seq)
            complement_str = str(bio_seq.complement())
            rev_complement_str = str(bio_seq.reverse_complement())
        else:
            complement_str = seq.translate(COMPLEMENT_TABLE)
            rev_complement_str = complement_str[::-1]

    return AnalyzeResponse(
        id=seq_id,
        description=seq_desc,
        length=length,
        counts=BaseCounts(A=a_count, T=t_count, G=g_count, C=c_count, N=n_count),
        gc_percent=gc_percent,
        at_percent=at_percent,
        molecular_weight_da=mw_da,
        molecular_weight_note=mw_note,
        gc_profile=gc_profile,
        records=record_metas,
        sequence=seq,
        complement=complement_str,
        reverse_complement=rev_complement_str,
    )
