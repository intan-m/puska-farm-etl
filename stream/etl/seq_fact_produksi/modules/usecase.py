from datetime import date
from typing import List, Optional

from etl.helper.api.schemas import MLTriggerProduksi

from etl.seq_fact_produksi.modules.entity import (
    ProduksiSusu,
    ProduksiTernak,
    FactProduksi,
)
from etl.seq_fact_produksi.modules.repository import (
    FactProduksiDWHRepository,
    FactProduksiMLRepository,
    FactProduksiWebSocketRepository,
)


class FactProduksiUsecase:
    UNIT_PETERNAKAN_MODELS_ID: List[int] = [
        10, # Zahran Farm
        11, # Wily Farm
        18, # NYX Farm
        23, # PROF Farm
    ]

    KABUPATEN_KOTA_MODELS_NAME: List[str] = [
        "PROBOLINGGO",
        "LUMAJANG"
    ]

    PROVINSI_MODELS_NAME: List[str] = [
        "JAWA TIMUR"
    ]
    
    __dwh_repo: FactProduksiDWHRepository
    __ml_repo: FactProduksiMLRepository
    __ws_repo: FactProduksiWebSocketRepository

    def __init__(
        self,
        dwh_repo: FactProduksiDWHRepository,
        ml_repo: FactProduksiMLRepository,
        ws_repo: FactProduksiWebSocketRepository,
    ):
        self.__dwh_repo = dwh_repo
        self.__ml_repo = ml_repo
        self.__ws_repo = ws_repo
    

    # Methods
    def get_or_create(
        self,
        tgl_produksi: date,
        id_unit_ternak: int,
        id_jenis_produk: int,
        sumber_pasokan: str,
    ) -> FactProduksi:
        fact_produksi_id = self.__dwh_repo.convert_id(tgl_produksi, id_unit_ternak, id_jenis_produk, sumber_pasokan)
        fact_produksi = self.__dwh_repo.get_or_create(fact_produksi_id)
        return fact_produksi


    def transform_susu(
        self,
        action: str,
        old_produksi: Optional[ProduksiSusu],
        new_produksi: Optional[ProduksiSusu],
        fact_produksi: FactProduksi
    ) -> FactProduksi:
        if action == "INSERT":
            _jumlah_produksi = fact_produksi.jumlah_produksi + new_produksi.jumlah
        elif action == "UPDATE":
            _jumlah_produksi = fact_produksi.jumlah_produksi - old_produksi.jumlah + new_produksi.jumlah
        elif action == "DELETE":
            _jumlah_produksi = fact_produksi.jumlah_produksi - old_produksi.jumlah
        
        fact_produksi.jumlah_produksi = _jumlah_produksi

        return fact_produksi


    def transform_ternak(
        self,
        action: str,
        old_produksi: Optional[ProduksiTernak],
        new_produksi: Optional[ProduksiTernak],
        fact_produksi: FactProduksi
    ) -> FactProduksi:
        if action == "INSERT":
            _jumlah_produksi = fact_produksi.jumlah_produksi + new_produksi.jumlah
        elif action == "UPDATE":
            _jumlah_produksi = fact_produksi.jumlah_produksi - old_produksi.jumlah + new_produksi.jumlah
        elif action == "DELETE":
            _jumlah_produksi = fact_produksi.jumlah_produksi - old_produksi.jumlah

        fact_produksi.jumlah_produksi = _jumlah_produksi
        
        return fact_produksi


    def load(self, fact_produksi: FactProduksi):
        self.__dwh_repo.load(fact_produksi)


    def predict_susu(self, tgl_prediksi: date, id_unit_peternakan: int, id_lokasi: int):
        id_waktu = self.__dwh_repo.get_id_waktu(tgl_prediksi)
        unit_peternakan_lokasi = self.__dwh_repo.get_unit_peternakan_lokasi(id_unit_peternakan)
        
        if (id_unit_peternakan in FactProduksiUsecase.UNIT_PETERNAKAN_MODELS_ID):
            trigger = MLTriggerProduksi(
                id_waktu = id_waktu,
                id_lokasi = id_lokasi,
                id_unit_peternakan = id_unit_peternakan,
            )
            self.__ml_repo.predict_susu(trigger)
        
        if (unit_peternakan_lokasi.label_provinsi in FactProduksiUsecase.PROVINSI_MODELS_NAME):
            trigger = MLTriggerProduksi(
                id_waktu = id_waktu,
                id_lokasi = unit_peternakan_lokasi.id_provinsi,
            )
            self.__ml_repo.predict_susu(trigger)
        
        if (unit_peternakan_lokasi.label_kabupaten_kota in FactProduksiUsecase.KABUPATEN_KOTA_MODELS_NAME):
            trigger = MLTriggerProduksi(
                id_waktu = id_waktu,
                id_lokasi = unit_peternakan_lokasi.id_kabupaten_kota,
            )
            self.__ml_repo.predict_susu(trigger)


    def push_websocket(self):
        self.__ws_repo.push_susu()
        self.__ws_repo.push_ternak()
