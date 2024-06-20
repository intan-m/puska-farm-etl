from pydantic import BaseModel
from datetime import date


# IDs
class FactProduksiID(BaseModel):
    id_waktu: int
    id_lokasi: int
    id_unit_peternakan: int
    id_jenis_produk: int
    id_sumber_pasokan: int


# DWH
class FactProduksi(FactProduksiID):
    jumlah_produksi: float


# OPS
class Produksi(BaseModel):
    tgl_produksi: date
    id_unit_ternak: int
    id_jenis_produk: int
    sumber_pasokan: str
    jumlah: float


# Kafka
class KafkaProduksi(BaseModel):
    source_table: str
    action: str
    data: Produksi
