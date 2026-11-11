#Aluno: João Antônio Dubeux
#Matricula: 20250027091
#Curso: Engenharia Eletrônica

"""le os dados do sensor (arquivo ou serial), computa o FFT e plota os graficos"""
import json
import sys

import matplotlib.pyplot as plt
import numpy as np

from data import DataSource, DataSourceError, FileSource, SerialSource

def load_config(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise DataSourceError(f"arquivo config não encontrado: {path}") from None
    except json.JSONDecodeError as e:
        raise DataSourceError(f"arquivo config invalid {path}: {e}") from None
    
def build_source(cfg: dict) -> DataSource:
    n = cfg["n_samples"]
    if cfg["source"] == "file":
        return FileSource(cfg["file"]["path"], n)
    if cfg["source"] == "serial":
        s = cfg["serial"]
        return SerialSource(s["port"], s["baudrate"], n, s["timeout"])
    raise DataSourceError(f"source desconhecida '{cfg['source']}' (use 'file' ou 'serial')")

def compute_fft(t: np.ndarray, v: np.ndarray):
    """retorna (frequencia, magnitude) do espectro unilateral"""
    dt = np.mean(np.diff(t))    #intervalo
    spectrum = np.fft.rfft(v) 
    freqs = np.fft.rfftfreq(len(v), d=dt) #hz
    magnitude = np.abs(spectrum) / len(v) #normaliza por N
    magnitude[1:] *= 2
    return freqs, magnitude

def plot(t, v, freqs, magnitude, save_to=None):
    fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=(12, 4))
    ax_t.plot(t, v)
    ax_t.set(title="Sinal no tempo", xlabel="Tempo (s)", ylabel="Voltagem (V)")
    ax_t.grid(True)
    ax_f.plot(freqs, magnitude)
    ax_f.set(title="FFT", xlabel="Frequencia (Hz)", ylabel="Amplitude (V)")
    ax_f.grid(True)
    fig.tight_layout()
    if save_to:
        fig.savefig(save_to, dpi=120)
    else:
        plt.show()

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    try:
        cfg = load_config(config_path)
        raw_t, raw_v = build_source(cfg).read()
    except DataSourceError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
 
    # Aplica os fatores para obter as unidades reais
    t = raw_t * cfg["time_scale"]
    v = raw_v * cfg["voltage_scale"]
 
    freqs, magnitude = compute_fft(t, v)
    peak = freqs[1:][np.argmax(magnitude[1:])]   # skip the DC bin
    print(f"{len(v)} amostras lidas. frequencia dominante: {peak:.3f} Hz")
    plot(t, v, freqs, magnitude)
 
 
if __name__ == "__main__":
    main()

            
    