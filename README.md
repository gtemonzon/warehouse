# Warehouse Module (MySQL)

Este proyecto define el **módulo de bodega** para controlar inventarios desde la **recepción**, **custodia** y **entrega** de bienes y suministros.

- DB: MySQL 8 (gratis, local vía Docker o instalación directa).
- Estándar de nombres: inglés, prefijo `tab_` para tablas, `vw_` para vistas y `sp_` para procedimientos.
- IDs: autoincrementales (INT), desde 1 en adelante.

## Estructura rápida
- `sql/schema.sql` — Tablas, índices, claves foráneas y vistas.
- `sql/procedures.sql` — Procedimientos para entradas/salidas individuales y por kits.
- `sql/sample_data.sql` — Datos de ejemplo mínimos.
- `docker-compose.yml` — MySQL 8 listo para levantar localmente.
- `.env.example` — Variables de entorno (ajústalas y renombra a `.env`).

## Pasos de instalación (rápido)
1. Instala Docker Desktop.
2. Copia `.env.example` a `.env` y ajusta contraseñas si deseas.
3. Ejecuta:
   ```bash
   docker compose up -d
   ```
4. Carga el esquema y procedimientos:
   ```bash
   docker exec -i warehouse-mysql mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < /docker-entrypoint-initdb.d/schema.sql
   docker exec -i warehouse-mysql mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < /docker-entrypoint-initdb.d/procedures.sql
   docker exec -i warehouse-mysql mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < /docker-entrypoint-initdb.d/sample_data.sql
   ```

## Flujo funcional
- **Productos** (`tab_product`) y **Bodegas** (`tab_warehouse`).
- **Kits** (`tab_kit`) con sus **componentes** (`tab_kit_item`). Un kit agrupa productos con cantidades definidas.
- **Transacciones** (`tab_product_transaction`) registran **entradas/salidas**. Las vistas calculan existencias actuales.
- **Fotos**: `tab_product`, `tab_warehouse`, `tab_kit` incluyen `photo` (LONGBLOB).
- **Documentos**: `tab_document` permite adjuntar múltiples PDF u otros archivos a cualquier registro (polimórfico).

## GitHub (creación de repo)
```bash
# dentro de /mnt/data/warehouse_project (o tu carpeta local)
git init
git add .
git commit -m "feat: initial warehouse schema, procedures, docker-compose"
git branch -M main
# crea un repo en GitHub llamado warehouse y luego:
git remote add origin https://github.com/<tu_usuario>/warehouse.git
git push -u origin main
```

## Nota sobre autenticación
Este módulo asume autenticación previa. Para pruebas rápidas incluye `tab_user` y procedimientos que **exigen** `user_id` (usuario seleccionado) en cada movimiento.
