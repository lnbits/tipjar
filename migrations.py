from lnbits.db import Database


async def m001_initial(db: Database):
    await db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS tipjar.TipJars (
            id {db.serial_primary_key},
            name TEXT NOT NULL,
            wallet TEXT NOT NULL,
            onchain TEXT,
            webhook TEXT
        );
        """
    )

    await db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS tipjar.Tips (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            sats {db.big_int} NOT NULL,
            tipjar {db.big_int} NOT NULL,
            FOREIGN KEY(tipjar) REFERENCES {db.references_schema}TipJars(id)
        );
        """
    )


async def m002_add_onchain_limit(db: Database):
    await db.execute(
        """
        ALTER TABLE tipjar.TipJars ADD COLUMN onchain_limit INTEGER;
        """
    )


async def m003_tipjar_id_string_rename_tables(db: Database):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS tipjar.tipjar (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            wallet TEXT NOT NULL,
            onchain TEXT,
            webhook TEXT,
            onchain_limit INTEGER
        );

        """
    )
    await db.execute(
        """
        INSERT INTO tipjar.tipjar (id, name, wallet, onchain, webhook, onchain_limit)
        SELECT id, name, wallet, onchain, webhook, onchain_limit
        FROM tipjar.TipJars;
        """
    )
    
    await db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS tipjar.tip (
            id TEXT PRIMARY KEY,
            tipjar TEXT NOT NULL,
            wallet TEXT NOT NULL,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            sats {db.big_int} NOT NULL
        );
        """
    )
    await db.execute(
        """
        INSERT INTO tipjar.tip (id, tipjar, wallet, name, message, sats)
        SELECT id, tipjar, wallet, name, message, sats
        FROM tipjar.Tips;
        """
    )
    await db.execute("DROP TABLE tipjar.Tips;")
    await db.execute("DROP TABLE tipjar.TipJars;")
