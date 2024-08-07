WITH cte_distribusi_susu AS (
  SELECT
    s.tgl_distribusi,
    s.id_unit_ternak AS id_unit_peternakan,
    s.id_mitra_bisnis,
    s.id_jenis_produk,
    ROUND(SUM(s.jumlah), 3) AS jumlah_distribusi,
    MIN(s.harga_berlaku) AS harga_minimum,
    MAX(s.harga_berlaku) AS harga_maximum,
    ROUND(AVG(s.harga_berlaku), 3) AS harga_rata_rata,
    ROUND(SUM(s.jumlah * s.harga_berlaku), 3) AS jumlah_penjualan
  FROM distribusi_susu_cdc AS s
  GROUP BY 1, 2, 3, 4
),
cte_distribusi_ternak AS (
  SELECT
    t.tgl_distribusi,
    t.id_unit_ternak AS id_unit_peternakan,
    t.id_mitra_bisnis,
    t.id_jenis_produk,
    ROUND(SUM(t.jumlah), 3) AS jumlah_distribusi,
    MIN(t.harga_berlaku) AS harga_minimum,
    MAX(t.harga_berlaku) AS harga_maximum,
    ROUND(AVG(t.harga_berlaku), 3) AS harga_rata_rata,
    ROUND(SUM(t.jumlah * t.harga_berlaku), 3) AS jumlah_penjualan
  FROM distribusi_ternak_cdc AS t
  GROUP BY 1, 2, 3, 4
),
cte_summary AS (
  SELECT
    tgl_distribusi,
    id_unit_peternakan,
    id_mitra_bisnis,
    id_jenis_produk,
    jumlah_distribusi,
    harga_minimum,
    harga_maximum,
    harga_rata_rata,
    jumlah_penjualan
  FROM (
    SELECT * FROM cte_distribusi_susu
    UNION ALL
    SELECT * FROM cte_distribusi_ternak
  ) AS ud
)
SELECT * FROM cte_summary
ORDER BY 1, 2, 3, 4;
