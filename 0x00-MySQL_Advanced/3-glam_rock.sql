-- Lists all brand with Glam rock ranked by longevity
SELECT band_name,
       2022 - formed AS lifespan
FROM metal_bands
WHERE split = 'Glam rock'
ORDER BY lifespan DESC;
