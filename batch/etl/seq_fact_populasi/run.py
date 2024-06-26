import sys
import pytz
from datetime import datetime, timedelta
from etl.helper import (
    db,
    id_getter,
    log,
)

from etl.seq_fact_populasi.modules.entity import (
    FactPopulasi,
    ParamsFactPopulasi,
)
from etl.seq_fact_populasi.modules.repository import (
    FactPopulasiDWHRepository,
    FactPopulasiOpsRepository,
)
from etl.seq_fact_populasi.modules.usecase import FactPopulasiUsecase


# Main Sequence
def main(
    params: ParamsFactPopulasi,
    log_batch_h: log.LogBatchHelper,
    id_getter_h: id_getter.IDGetterHelper,
    usecase: FactPopulasiUsecase
):
    """
    Fact Populasi - Batch ETL

    Params:
        - START_DATE [str]. Start date of data processing in format '%Y-%m-%d' (default: 7 days ago)
        - END_DATE [str]. End date of data processing (include) in format '%Y-%m-%d' (default: today)
    """
    
    try:
        log_batch_h.start_log("fact_populasi", params)
        
        fact_populasi_calc = usecase.get(params)
        fact_populasi = [
            FactPopulasi(
                id_waktu = id_getter_h.get_id_waktu(row.tgl_pencatatan),
                id_lokasi = id_getter_h.get_id_lokasi_from_peternakan(row.id_peternakan),
                id_peternakan = row.id_peternakan,
                jenis_kelamin = row.jenis_kelamin,
                tipe_ternak = row.tipe_ternak,
                tipe_usia = row.tipe_usia,
                jumlah_lahir = row.jumlah_lahir,
                jumlah_mati = row.jumlah_mati,
                jumlah_masuk = row.jumlah_masuk,
                jumlah_keluar = row.jumlah_keluar,
                jumlah = row.jumlah,
            )
            for row in fact_populasi_calc
        ]
        processed_row_count = usecase.load(fact_populasi)
        
        log_batch_h.end_log(processed_row_count)
        logger.info(f"Processed - Status: OK (Affected: {processed_row_count} row count)")
    except Exception as err:
        logger.error(str(err))
        logger.info("Processed - Status: FAILED")


# Runtime
if __name__ == "__main__":
    logger = log.create_logger()
    dwh = db.DWHHelper()
    ops = db.OpsHelper()
    
    log_batch_h = log.LogBatchHelper(dwh)
    id_getter_h = id_getter.IDGetterHelper(dwh, logger)
    
    dwh_repo = FactPopulasiDWHRepository(dwh, logger)
    ops_repo = FactPopulasiOpsRepository(ops, logger)
    usecase = FactPopulasiUsecase(dwh_repo, ops_repo, logger)

    # Get runtime params
    _, *sys_params = sys.argv
    start_date, end_date = sys_params + [None] * (2-len(sys_params))
    start_date = start_date if (start_date) else (datetime.now(pytz.timezone("Asia/Jakarta")) - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = end_date if (end_date) else datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d")

    params = ParamsFactPopulasi(
        start_date = start_date,
        end_date = end_date,
    )

    main(
        params,
        log_batch_h = log_batch_h,
        id_getter_h = id_getter_h,
        usecase = usecase,
    )
