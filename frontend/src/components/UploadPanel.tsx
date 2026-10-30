import React, { useState } from 'react';
import { postAnalyze } from '../lib/api';
import { MAX_FILE_BYTES } from '../lib/sequenceUtils';
import { useGenomeStore } from '../store/useGenomeStore';

const SAMPLE_GFP = `>GFP_synthetic_construct|length=420bp Engineered Aequorea victoria green fluorescent protein mini-ORF
ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTGCCCATCCTGGTCGAGCTGGAC
GGCGACGTAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGATGCCACCTAC
GGCAAGCTGACCCTGAAGTTCATCTGCACCACCGGCAAGCTGCCCGTGCCCTGGCCCACC
CTCGTGACCACCCTGACCTACGGCGTGCAGTGCTTCAGCCGCTACCCCGACCACATGAAG
CAGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTCCAGGAGCGCACCATCTTC
TTCAAGGACGACGGCAACTACAAGACCCGCGCCGAGGTGAAGTTCGAGGGCGACACCCTG
GTGAACCGCATCGAGCTGAAGGGCATCGACTTCAAGGAGGACGGCAACATCCTGGGGCAC
AAGCTGGAGTACAACTACAACAGCCACAACGTCTATATCATGGCCGACAAGCAGAAGAAC`;

export const UploadPanel: React.FC = () => {
  const { rawInputText, analysis, analyzeError, setRawInputText, setAnalysis, setAnalyzeStatus } =
    useGenomeStore();
  const [pasteValue, setPasteValue] = useState<string>('');
  const [isDragging, setIsDragging] = useState<boolean>(false);

  async function runAnalyze(text: string, recordId?: string): Promise<void> {
    setRawInputText(text);
    setAnalyzeStatus('loading');
    try {
      const result = await postAnalyze({
        sequence: text,
        sequence_id: recordId ?? null,
        include_complements: false,
        gc_window_size: 100,
      });
      setAnalysis(result);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unable to analyze sequence.';
      setAnalyzeStatus('error', msg);
    }
  }

  function handleFile(file: File): void {
    if (file.size > MAX_FILE_BYTES) {
      setAnalyzeStatus('error', 'File exceeds the 5 MB limit. Upload a FASTA file under 5 MB.');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      void runAnalyze(String(reader.result ?? ''));
    };
    reader.readAsText(file);
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) handleFile(file);
      }}
      className={`flex flex-col gap-3 ${isDragging ? 'bg-white p-2 border border-[#1A1F24]' : ''}`}
    >
      <div className="flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={() => void runAnalyze(SAMPLE_GFP)}
          className="bg-[#E4572E] text-white px-3 py-1.5 rounded-[4px] text-[15px]"
        >
          Load sample
        </button>

        <label className="hover:underline cursor-pointer text-[15px]">
          <span>Choose .fasta, .fa, or .txt file</span>
          <input
            type="file"
            accept=".fasta,.fa,.txt"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) handleFile(f);
            }}
          />
        </label>

        {analysis && analysis.records.length > 1 && (
          <div className="flex items-center gap-2">
            <label htmlFor="recordDropdown" className="text-[13px] text-[#6B7680]">
              Record
            </label>
            <select
              id="recordDropdown"
              value={analysis.id}
              onChange={(e) => void runAnalyze(rawInputText, e.target.value)}
              className="bg-white border border-[#E3E7EA] rounded-[4px] px-2.5 py-1 text-[15px] font-mono"
            >
              {analysis.records.map((rec) => (
                <option key={rec.id} value={rec.id}>
                  {rec.id} ({rec.length} bp)
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        <input
          type="text"
          value={pasteValue}
          onChange={(e) => setPasteValue(e.target.value)}
          placeholder="Paste FASTA or raw A, T, G, C, N sequence (or drag & drop a file here)"
          className="flex-1 bg-white border border-[#E3E7EA] rounded-[4px] px-3 py-1.5 text-[15px] font-mono"
        />
        <button
          type="button"
          onClick={() => void runAnalyze(pasteValue)}
          className="hover:underline text-[15px]"
        >
          Analyze pasted
        </button>
      </div>

      {analyzeError && <p className="text-[13px] text-[#D64545] m-0">{analyzeError}</p>}
    </div>
  );
};
