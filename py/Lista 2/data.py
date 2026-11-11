#Fontes de dados para o funcionamento dos sensores, as classes utilizam o read() que retornam um par de arrays numpy com os inteiros

from abc import ABC, abstractmethod

import numpy as np
# Uma amostra = 2 bytes de tempo + 2 bytes de voltagem
#tempo nao atribuido, voltagem atribuida 
SAMPLE_DTYPE = np.dtype([("time", "<u2"), ("voltage", "<i2")])

class DataSourceError(Exception):
    "problemas para recolher os dados"
    
def decode(raw: bytes, n_samples:int) -> tuple[np.ndarray, np.ndarray]:
    #transforma bytes raw em (tempo, voltagem) arrays de inteiros, checando o tamanho 
    expected = n_samples * SAMPLE_DTYPE.itemsize
    if len(raw) != expected:
        raise DataSourceError(
            f"sequencia de tamanho errada: expected {expected} bytes"
            f"({n_samples} samples), got {len(raw)} bytes"
        )
    samples = np.frombuffer(raw, dtype=SAMPLE_DTYPE)
    return samples["time"], samples["voltage"]

class DataSource(ABC):
    @abstractmethod
    def read(self) -> tuple[np.ndarray, np.ndarray]:
        # retorna (raw_time, raw_voltage) em uma sequência inteira
        raise NotImplementedError

class FileSource(DataSource):
    def __init__(self, path: str, n_samples: int):
        self.path = path
        self.n_samples = n_samples
        
    def read(self) -> tuple[np.ndarray, np.ndarray]:
        try:
            with open(self.path, "rb") as f:
                raw = f.read()
        except FileNotFoundError:
            raise DataSourceError(f"Arquivo não encontrado: {self.path}") from None
        except OSError as e:
            raise DataSourceError(f"Não pode ler {self.path}: {e}") from None
        return decode(raw, self.n_samples)

class SerialSource(DataSource):
    def __init__(self, port: str, baudrate: int, n_samples: int,
                 timeout: float = 0.5):
        self.port = port
        self.baudrate = baudrate
        self.n_samples = n_samples
        # os gaps devem ser menores que 1 segundo, porem maiores que a pausa entre os bytes da sequenquencia
        self.timeout = timeout
 
    def read(self) -> tuple[np.ndarray, np.ndarray]:
        try:
            import serial  # importa aqui para que funcione sem o  pyserial
        except ImportError:
            raise DataSourceError(
                "pyserial is not installed (pip install pyserial).") from None
 
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        except serial.SerialException as e:
            raise DataSourceError(
                f"não pode acessar a porta serial {self.port}: {e}") from None
 
        with ser:
            ser.reset_input_buffer()
 
            # 1) pode ter começado no meio da sequência: descarta
            #  os  bytes.
            while ser.read(1):
                pass
 
            # 2) espera pelo primeiro byte da proxima sequencia. o gap dura 1 segundo e uma parte ja passou, entao pode ter tempo extra
            ser.timeout = 3 * self.timeout
            first = ser.read(1)
            if not first:
                raise DataSourceError(
                    "Nenhum dado recebido apos o gap (O sensor esta ligado ?).")
 
            # 3) le o resto da sequencia com o timeout normal.
            ser.timeout = self.timeout
            expected = self.n_samples * SAMPLE_DTYPE.itemsize
            raw = first + ser.read(expected - 1)
        return decode(raw, self.n_samples)
 
