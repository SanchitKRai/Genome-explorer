import { describe, expect, it } from 'vitest';
import {
  computeSlidingGc,
  countBases,
  parseFastaText,
  validateDnaSequence,
} from './sequenceUtils';

describe('sequenceUtils Phase 2 unit tests', () => {
  it('parses multi-record FASTA text', () => {
    const fasta = '>rec1 first record\nATGC\n>rec2 second record\nGGCCAA';
    const records = parseFastaText(fasta);
    expect(records.length).toBe(2);
    expect(records[0].id).toBe('rec1');
    expect(records[1].rawSequence).toBe('GGCCAA');
  });

  it('flags RNA U characters with position', () => {
    const res = validateDnaSequence('ATGCUAA');
    expect(res.valid).toBe(false);
    expect(res.errorCode).toBe('RNA_DETECTED');
    expect(res.errorMessage).toContain('position 5');
  });

  it('flags first invalid character with exact 1-based position', () => {
    const res = validateDnaSequence('atgc\n gcat#aa');
    expect(res.valid).toBe(false);
    expect(res.errorCode).toBe('INVALID_BASE');
    expect(res.errorMessage).toContain("'#' at position 9");
  });

  it('computes base counts and 100bp sliding window GC%', () => {
    const seq = 'G'.repeat(50) + 'A'.repeat(50) + 'C'.repeat(50);
    const counts = countBases(seq);
    expect(counts).toEqual({ A: 50, T: 0, G: 50, C: 50, N: 0 });
    const profile = computeSlidingGc(seq, 100);
    expect(profile.length).toBeGreaterThan(0);
    expect(profile[0].gc_percent).toBe(50);
  });
});
