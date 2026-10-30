import { BaseCounts, FastaRecordMeta, GcWindowPoint } from './api';

export interface ParsedFastaRecord {
  id: string;
  description: string;
  rawSequence: string;
}

export interface ValidationOutcome {
  valid: boolean;
  cleanedSequence: string;
  errorCode: string | null;
  errorMessage: string | null;
}

const ALLOWED = new Set(['A', 'T', 'G', 'C', 'N']);
export const MAX_FILE_BYTES = 5 * 1024 * 1024;
export const MAX_SEQUENCE_BP = 100_000;

export function parseFastaText(rawText: string): ParsedFastaRecord[] {
  const trimmed = rawText.trim();
  if (!trimmed) return [];
  if (!trimmed.startsWith('>')) {
    return [{ id: 'seq_1', description: 'Pasted DNA sequence', rawSequence: trimmed }];
  }
  const records: ParsedFastaRecord[] = [];
  let currentId = '';
  let currentDesc = '';
  let lines: string[] = [];

  for (const rawLine of trimmed.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) continue;
    if (line.startsWith('>')) {
      if (currentId) {
        records.push({ id: currentId, description: currentDesc, rawSequence: lines.join('') });
      }
      const header = line.slice(1).trim();
      const firstSpace = header.search(/\s/);
      currentId = firstSpace === -1 ? header || `record_${records.length + 1}` : header.slice(0, firstSpace);
      currentDesc = header;
      lines = [];
    } else {
      lines.push(line);
    }
  }
  if (currentId) {
    records.push({ id: currentId, description: currentDesc, rawSequence: lines.join('') });
  }
  return records;
}

export function validateDnaSequence(rawSeq: string): ValidationOutcome {
  const cleaned = rawSeq.replace(/\s+/g, '').toUpperCase();
  if (!cleaned) {
    return {
      valid: false,
      cleanedSequence: '',
      errorCode: 'EMPTY_SEQUENCE',
      errorMessage: 'Sequence contains no nucleotides. Provide a DNA sequence with A, T, G, C, or N.',
    };
  }
  if (cleaned.length > MAX_SEQUENCE_BP) {
    return {
      valid: false,
      cleanedSequence: '',
      errorCode: 'SEQUENCE_TOO_LONG',
      errorMessage: `Sequence length (${cleaned.length.toLocaleString()} bp) exceeds the V1 maximum of 100,000 bp. Trim the sequence to 100,000 bp or fewer.`,
    };
  }
  for (let i = 0; i < cleaned.length; i++) {
    const ch = cleaned[i];
    if (!ALLOWED.has(ch)) {
      if (ch === 'U') {
        return {
          valid: false,
          cleanedSequence: '',
          errorCode: 'RNA_DETECTED',
          errorMessage: `Character 'U' at position ${i + 1} indicates this sequence looks like RNA. Convert U to T to analyze DNA.`,
        };
      }
      return {
        valid: false,
        cleanedSequence: '',
        errorCode: 'INVALID_BASE',
        errorMessage: `Invalid character '${ch}' at position ${i + 1}. Only A, T, G, C, and N are allowed.`,
      };
    }
  }
  return { valid: true, cleanedSequence: cleaned, errorCode: null, errorMessage: null };
}

export function computeSlidingGc(seq: string, windowSize = 100): GcWindowPoint[] {
  if (!seq.length) return [];
  const win = Math.min(windowSize, seq.length);
  const step = seq.length > win ? Math.max(1, Math.floor((seq.length - win) / 50)) : 1;
  const out: GcWindowPoint[] = [];
  for (let pos = 0; pos <= seq.length - win; pos += step) {
    const slice = seq.slice(pos, pos + win);
    let gc = 0;
    let nonN = 0;
    for (let i = 0; i < slice.length; i++) {
      const b = slice[i];
      if (b === 'G' || b === 'C') gc++;
      if (b !== 'N') nonN++;
    }
    out.push({
      position: pos + 1,
      gc_percent: nonN > 0 ? Number(((gc / nonN) * 100).toFixed(2)) : 0,
    });
    if (seq.length === win) break;
  }
  return out;
}

export function countBases(seq: string): BaseCounts {
  const counts: BaseCounts = { A: 0, T: 0, G: 0, C: 0, N: 0 };
  for (let i = 0; i < seq.length; i++) {
    const ch = seq[i] as keyof BaseCounts;
    if (counts[ch] !== undefined) counts[ch]++;
  }
  return counts;
}

export function toRecordMetas(records: ParsedFastaRecord[]): FastaRecordMeta[] {
  return records.map((r) => ({
    id: r.id,
    description: r.description,
    length: r.rawSequence.replace(/\s+/g, '').length,
  }));
}
