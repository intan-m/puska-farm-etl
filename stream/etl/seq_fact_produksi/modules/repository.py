import os
import json
from typing import Optional
from datetime import date
from logging import Logger
from typing import List

from etl.helper.db import DWHHelper
from etl.helper.api.ml_api import MLAPIHelper
from etl.helper.id_getter import IDGetterHelper
from etl.helper.websocket import WebSocketHelper

from etl.helper.api.schemas import MLTriggerProduksi

from etl.seq_fact_produksi.modules.entity import (
    FactProduksi,
    FactProduksiID,
    UnitPeternakanLokasi,
)


class FactProduksiDWHRepository:
    __dwh: DWHHelper
    __logger: Logger
    __id_getter: IDGetterHelper
    __query_dir: str

    PK: List[str] = [
        "id_waktu",
        "id_lokasi",
        "id_unit_peternakan",
        "id_jenis_produk",
    ]

    def __init__(self, dwh: DWHHelper, logger: Logger):
        self.__dwh = dwh
        self.__logger = logger

        self.__id_getter = IDGetterHelper(dwh, logger)
        self.__query_dir = os.path.join(os.path.dirname(__file__), "query")


    # Methods
    def convert_id(
        self,
        tgl_produksi: date,
        id_unit_ternak: int,
        id_jenis_produk: int,
        sumber_pasokan: str,
    ) -> FactProduksiID:
        fact_produksi_id = FactProduksiID(
            id_waktu = self.__id_getter.get_id_waktu(tgl_produksi),
            id_lokasi = self.__id_getter.get_id_lokasi_from_unit_peternakan(id_unit_ternak),
            id_unit_peternakan = id_unit_ternak,
            id_jenis_produk = id_jenis_produk,
            id_sumber_pasokan = self.__id_getter.get_id_sumber_pasokan(sumber_pasokan),
        )
        return fact_produksi_id


    def get_or_create(self, fact_produksi_id: FactProduksiID) -> FactProduksi:
        self.__logger.debug("Get data from 'Fact Produksi'")
        results = self.__dwh.run(self.__query_dir, "get_fact_produksi.sql", fact_produksi_id.model_dump())
        
        if (results):
            fact_produksi = FactProduksi(**results[0])
        else:
            fact_produksi = FactProduksi(
                **fact_produksi_id.model_dump(),
                jumlah_produksi = 0,
            )
        return fact_produksi


    def get_id_waktu(self, _dt: date) -> Optional[int]:
        self.__logger.debug(f"Get id_waktu from tanggal: {_dt.strftime('%Y-%m-%d')}")
        id_waktu = self.__id_getter.get_id_waktu(_dt)
        return id_waktu
    
    def get_unit_peternakan_lokasi(self, id_unit_peternakan: int) -> Optional[UnitPeternakanLokasi]:
        self.__logger.debug(f"Get lokasi from unit_peternakan: {id_unit_peternakan}")
        result = self.__id_getter.get_unit_peternakan_lokasi(id_unit_peternakan)

        if (result):
            return UnitPeternakanLokasi.model_validate(result)
        return result


    def load(self, produksi: FactProduksi):
        self.__logger.debug("Load data to 'Fact Produksi'")
        self.__dwh.load(
            "fact_produksi_stream",
            data = [produksi],
            pk = self.PK,
            update_insert = True
        )


class FactProduksiMLRepository:
    __ml_api: MLAPIHelper
    __logger: Logger

    def __init__(self, ml_api: MLAPIHelper, logger: Logger):
        self.__ml_api = ml_api
        self.__logger = logger
    
    def predict_susu(self, trigger: MLTriggerProduksi):
        self.__logger.debug("Predict Produksi Susu")
        error = self.__ml_api.predict_susu(trigger)
        if error:
            self.__logger.error(f"Failed to trigger ML: {error}")


class FactProduksiWebSocketRepository:
    __ws: WebSocketHelper
    __logger: Logger

    def __init__(self, ws: WebSocketHelper, logger: Logger):
        self.__ws = ws
        self.__logger = logger
    
    def push_susu(self):
        self.__logger.debug("Push to WebSocket: etl-susu")
        payload = {
            "type": "etl-susu",
        }
        self.__ws.push(json.dumps(payload))

    def push_ternak(self):
        self.__logger.debug("Push to WebSocket: etl-ternak")
        payload = {
            "type": "etl-ternak",
        }
        self.__ws.push(json.dumps(payload))
