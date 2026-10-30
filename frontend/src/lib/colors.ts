export type NucleotideBase = 'A' | 'T' | 'G' | 'C' | 'N';

export const BASE_COLORS: Record<NucleotideBase, string> = {
  A: '#2F9E5F',
  T: '#D64545',
  G: '#E3B023',
  C: '#2F6FDE',
  N: '#6B7680',
};

export const UI_PALETTE = {
  background: '#FFFFFF',
  surface: '#F5F6F7',
  ink: '#1A1F24',
  secondary: '#6B7680',
  hairline: '#E3E7EA',
  accent: '#E4572E',
  backbone: '#B8C0C6',
} as const;

export const BASE_COMPLEMENT: Record<NucleotideBase, NucleotideBase> = {
  A: 'T',
  T: 'A',
  G: 'C',
  C: 'G',
  N: 'N',
};
